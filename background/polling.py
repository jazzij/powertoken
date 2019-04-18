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
from datetime import datetime
from database import db_session, close_connection
from data.models import Activity, Event, Log, User, Day
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
		
		#logging.debug(activity_events)
		num_completed = weconnect.update_db_events(activity_events, db_session)
		#logging.debug("{} {}".format(num_completed, len(activity_events)))

		#PROGRESS TALLY --- THIS WILL BE HANDLED BY A LISTENER EVENTUALLY
		num_activities = float(len(activity_events))
		percentageProgress = num_completed / num_activities
		logging.info("Today's Percentage Progress for {} is {}".format(user, percentageProgress))
		
		tallyProgress = None
		
		weightedProgress = None
		
		
		# Send progress to Fitbit
		step_count = fitbit.update_progress_decimal(user, percentageProgress)
		logging.info("Just added {} steps to {}'s account!".format(step_count, user.username))
		
		# Add a Log object to the database
		#log = Log(wc_progress=progress, fb_step_count=step_count, user=user)
	
		# on the last poll of the day, create Day total
		cur_time = datetime.now().time()
		if cur_time > LAST_POLL_TIME:
			save_today(user, num_completed, percentageProgress, db_session)
		
	db_session.commit()	
	close_connection()


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
		
