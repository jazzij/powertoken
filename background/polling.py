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
from database import get_session, close_connection
#from data.models import Activity, Event, Log, User, Day
from database import Activity, Event, Log, User, Day
#from database import TALLY, CHARGE, WEIGHT, PLAN
import fitbit
import weconnect

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

LAST_POLL_TIME = datetime.strptime('14:30', '%H:%M').time()

TALLY="tally"
CHARGE="charge"
WEIGHT="weight"
PLAN="plan"

import atexit
def onExit():
	close_connection()
atexit.register(onExit)


def poll_and_save():
	"""
	Check for new events (and activities) for every saved user and save them to the database 
	"""
	db_session = get_session()
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
	db_session = get_session()
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

		#CALCULATE PROGRESS, BASED ON INDIVIDUAL METAPHOR
		progress = 0
		if user.metaphor == PLAN:			
			#BASIC PLAN --- PERCENTAGE COMPLETE VS PLANNED
			progress = calculate_progress_plan(num_completed, event_ids)
			logging.info("Today's Percentage Progress for {} is {}".format(user, progress))
			
			# Send progress to Fitbit
			step_count = fitbit.update_progress_decimal(user, progress, db_session)
			logging.info("Just added {} steps to {}'s account!".format(step_count, user.username))
		
		elif user.metaphor == WEIGHT:		
			#WEIGHTED PROGRESS
			progress = calculate_progress_weight(event_ids, db_session)
			logging.info("Today's Weighted Progress for {} is {}".format(user, progress))
		
			# Send progress to Fitbit
			step_count = fitbit.update_progress_decimal(user, progress, db_session)
			logging.info("Just added {} steps to {}'s account!".format(step_count, user.username))
					
		elif user.metaphor == TALLY:
			# TALLY - BASIC COUNT	
			progress = calculate_progress_tally(num_completed, event_ids)
			logging.info("Today's TALLY Progress for {} is {}".format(user, progress))
			
			# Send progress to Fitbit
			step_count = fitbit.update_progress_count(user, progress)
			logging.info("Just added {} steps to {}'s account!".format(step_count, user.username))
						
			
		elif user.metaphor == CHARGE:
			# CHARGE - WEIGHTED COUNT
			progress = calculate_progress_charge(num_completed, event_ids, session) 
			logging.info("Today's CHARGE Progress for {} is {}".format(user, progress))
		
			# Send progress to Fitbit
			step_count = fitbit.update_progress_count(user, progress)
			logging.info("Just added {} steps to {}'s account!".format(step_count, user.username))
					
		
		# Add a Log object to the database
		#log = Log(wc_progress=progress, fb_step_count=step_count, user=user)
	
		# on the last poll of the day, create Day total for the user
		cur_time = datetime.now().time()
		if cur_time > LAST_POLL_TIME:
			save_today(user, num_completed, progress, db_session)
		
	db_session.commit()	
	close_connection()

	

def calculate_progress_plan(num_events_completed, event_id_list):
	progress = num_events_completed / float(len(event_id_list))
	return progress #percentage
		
def calculate_progress_weight(event_id_list, session):
	target= 0
	completed=0
	evs = session.query(Event).filter(Event.eid.in_(event_id_list)).all()
	for ev in evs:
		weight = ev.activity.weight
		target += weight
		if ev.completed:
			completed += weight

	progress = completed / float(target)
	#logging.info("weighted progress: {} / {} = {}".format(completed, target, progress ))
	return progress #percentage

def calculate_progress_tally(num_completed, event_id_list):
	max_steps = fitbit.DEFAULT_GOAL
	activity_value = max_steps / 5 # number of LED's visible
	return num_completed * activity_value		#raw number of steps

def calculate_progress_charge(num_completed, event_id_list, session):
	max_steps = fitbit.DEFAULT_GOAL
	activity_value = fitbit.STEPS_PER_POINT
	total = 0
	evs = session.query(Event).filter(Event.eid.in_(event_id_list)).all()
	for ev in evs:
		weight = ev.activity.weight
		if ev.completed:
			weighted_value = activity_value * weight
			total += weighted_value
	return total	


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

def weighted_tally(user, session):
	pass


def weekly_weighted(user, session):
	#get user's progress from last 7 days (assume weighted progress)
	pass

if __name__ == "__main__":
		
	if len(sys.argv) == 1:
		poll_and_save()
	
	elif int(sys.argv[1]) == 0:
		logging.info("Initiating first poll of the day...")
		poll_and_save()
	elif int(sys.argv[1]) == 1:
		logging.info("Initiating update poll at {}".format(datetime.now()))
		poll_and_update()

	#debug option
	elif int(sys.argv[1]) == 3:
		result = calculate_progress_plan( 3, [1,2,3,4,5])
		print(result)
		result = calculate_progress_tally(3, [1,2,3,4,5])
		print(result)

