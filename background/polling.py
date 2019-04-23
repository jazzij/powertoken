"""
Script that runs the main PowerToken function: poll WEconnect and update Fitbit.
Meant to be run in Crontab, probably every 5-15 minutes.\n

USAGE:
First poll of the day adds new events (poll_and_save)
Subsequent polls should update completion status (poll_and_update)

Created by Abigail Franz on 2/28/2018.\n
Last modified by Jasmine J on 4/2019.

"""
import sys
import math
from datetime import datetime
from database import db_session, close_connection
from data.models import Activity, Event, Log, User, Day
from data.models import TALLY, PROGRESS, WEIGHT, CHARGE
import fitbit
import weconnect
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

LAST_POLL_TIME = datetime.strptime('14:30', '%H:%M').time()

import atexit
def onExit():
	db_session.close()
atexit.register(onExit)

def poll_and_save():
	"""
	Check for new events (and activities) for every saved user and save them to the database 
	"""
	users = db_session.query(User).all()
	for user in users:
		logging.debug("Polling for {}".format(user))
		
		#Gather events from WC and save to database, including updating new activities added
		activity_events = weconnect.get_todays_events(user, db_session)
		weconnect.add_events_to_db(activity_events, db_session)
		logging.info("Found {} new events for user {}".format(len(activity_events), user.wc_id))
	
	logging.info("Completed first POLL for {} users at {}.".format(len(users), datetime.now()))
	
	db_session.commit()
	close_connection()

def poll_and_update():
	"""
	For each user in the database:
	1. Poll WEconnect to update how many of the user's events for today
	   have been completed.
	---
	2. Compute the user's progress for today.
	2. If the user has made progress since the last time this script was run,
	   send the new progress to Fitbit as a walking activity with the following
	   number of steps: progress * 1,000,000.
	"""
	
	users = db_session.query(User).all()
	
	for user in users:
		logging.info("polling for {}".format(user))
		# API call to WEconnect activities-with-events
		activity_events = weconnect.get_todays_events(user, db_session)
		if len(activity_events) < 1: 
			continue
		
		#Update all events in the DB
		num_completed, event_ids = weconnect.update_db_events(activity_events, db_session)
		logging.debug("Num activities completed: {} out of {}".format(num_completed, len(activity_events)))

		#TALLY
		progress = 0
		if user.goal_period == TALLY:
			progress = num_completed
			logging.info("Tally progress: {}".format(progress))
			
		elif user.goal_period == PROGRESS:			
			#BASIC PROGRESS --- THIS WILL BE HANDLED BY A LISTENER EVENTUALLY
			num_activities = float(len(activity_events))
			progress = num_completed / num_activities
			logging.info("Today's Percentage Progress for {} is {}".format(user, progress))

		elif user.goal_period == WEIGHT:		
			#WEIGHTED PROGRESS
			progress = weighted_progress(user, event_ids, db_session)
			logging.info("Today's Weighted Progress for {} completed activities = {}".format(num_completed, progress))
		
		elif user.goal_period == CHARGE:	
			pass
		
		
		# Send progress to Fitbit
		#step_count = fitbit.update_progress_decimal(user, progress)
		#logging.info("Just added {} steps to {}'s account!".format(step_count, user.username))
		
		# Add a Log object to the database
		#log = Log(wc_progress=progress, fb_step_count=step_count, user=user)
	
		# on the last poll of the day, create Day total
		#cur_time = datetime.now().time()
		#if cur_time > LAST_POLL_TIME:
		#	save_today(user, num_completed, progress, db_session)
		
	db_session.commit()	
	close_connection()


def weighted_progress(user, event_ids, session):
	target= 0
	completed=0
	evs = session.query(Event).filter(Event.eid.in_(event_ids)).all()
	for ev in evs:
		weight = ev.activity.weight
		target += weight
		if ev.completed:
			completed += weight

	progress = completed / target
	logging.info("{}'s weighted progress: {} / {} = {}".format(user, completed, target, progress ))
	return progress
	
#def weighted_progress(user):
#	target=0        #target=sum(all events for one day * their weights)
#	completed=0     #completed=sum(completed events * their weights)
#	today = datetime.now()
#	activities=user.activities.all()
#	for activity in activities:
#		logging.debug("Activity {} with weight {}".format(activity.name, activity.weight))
#		event=activity.events.filter_by(start_time=today.date()).first()
#		if event.completed is True:
#			target+=activity.weight
#		for event in events:
#			if(event.start_time.date()==today.date()):
#				event.completed = True
#				target+=activity.weight
#				if(event.completed==True):
#					completed+=activity.weight
#	if target > 0:
#		logging.debug("{} weighted_Progress: {} \ {}".format(user, completed, target))
#		return completed/target



def save_today(user, checkin_count, today_progress, session):
	'''
	on Last Poll, create a new DAY for the user, save the calculated checkin count and progress 
	'''
	thisDay = Day(user_id=user.id, date=datetime.now().date(), computed_progress=today_progress, checkin_count=checkin_count)
	db_session.add(thisDay)
	db_session.commit()

	today_events = weconnect.get_events_for_user(user, db_session)
	logging.debug(today_events)
	for ev in today_events:
		ev.day_id = thisDay.id
		logging.debug(ev.day_id)	
	db_session.commit()



if __name__ == "__main__":
	if len(sys.argv) == 1:
		poll_and_save()
	
	elif int(sys.argv[1]) == 0:
		logging.info("Initiating first poll of the day...")
		poll_and_save()
	elif int(sys.argv[1]) == 1:
		logging.info("Initiating update poll at {}".format(datetime.now()))
		poll_and_update()
		
