"""
Script that runs the main PowerToken function: poll WEconnect and update Fitbit.
Meant to be run in Crontab, probably every 5-15 minutes.\n

USAGE:
First poll of the day adds new events (poll_and_save)
Subsequent polls should update completion status (poll_and_update)

Created by Abigail Franz on 2/28/2018.\n
Last modified by Jasmine J on 6/2019.

"""
import sys
import math
import csv
from datetime import datetime
from database import get_session, close_connection
from database import Activity, Event, User, Day
from database import TALLY, CHARGE, WEIGHT, PLAN
import fitbit
import weconnect

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

LAST_POLL_TIME = datetime.strptime('23:30', '%H:%M').time()

TALLY="tally"
CHARGE="charge"
WEIGHT="weight"
PLAN="plan"

#import atexit
#def onExit():
#	close_connection()
#atexit.register(onExit)


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

		# Add "progress" based on metaphor
		step_count = 0
		if user.metaphor == CHARGE:
			#get yesterDay
			yesterDay = user.yesterday()
			if yesterDay is not None:
				#get progress from yesterDay, add as starting progress to Fitbit
				step_count = fitbit.update_progress_count(user, yesterDay.computed_progress, db_session)
				logging.info("Just added {} prelim steps to {}'s account!".format(step_count, user.username))
			else:
				logging.info("CHARGE: Starting fresh from today: {}".format(datetime.now()))
		
		#Setup new DAY for each user
		newDay = create_today(user, 0, step_count, db_session)
		
	logging.info("Completed first POLL for {} users at {}.".format(len(users), datetime.now()))
	
	db_session.commit()
	close_connection(db_session)

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
	timestamp = datetime.now()
	for user in users:
		logging.info("polling for {}".format(user))
		
######	#if a user for some reason doesn't have DAY setup, then rerun poll_and_save for all
		today = user.thisday()
		if today is None:
			poll_and_save()
			today = user.thisday()
			logging.info ("{} was incomplete. Ran poll-save to add {} day".format(user, today))
#######
			
		# API call to WEconnect activities-with-events
		activity_events = weconnect.get_todays_events(user, db_session)
		if len(activity_events) < 1: 
			continue
		
		#Update all events in the DB
		num_completed, event_ids = weconnect.update_db_events(activity_events, db_session)
		logging.debug("Num activities completed: {} out of {}".format(num_completed, len(activity_events)))

		#calculate progress if there is a change
		if len(event_ids) > 0:
			logging.debug("detected {} vs {}".format(num_completed, today.complete_count))
			if num_completed <= today.complete_count:
				logging.info("No more progress made yet.")
			else:	
				#CALCULATE PROGRESS, BASED ON INDIVIDUAL METAPHOR
				progress, step_count = calculate_progress( user, num_completed, event_ids, db_session)
				logging.info("{} made {} progress today, with a updated step count of {}".format(user.username, progress, step_count))
		
		#log today
		printout(user, timestamp)
			
		# on the last poll of the day, create Day total for the user
		#cur_time = datetime.now().time()
		#if cur_time > LAST_POLL_TIME:
		#	save_today(user, num_completed, progress, db_session)
		#save_today(user, num_completed, progress, db_session)

	close_connection(db_session)


def calculate_progress(user, num_completed, event_ids, session):
	progress = 0
	step_count = 0	
	if user.metaphor == PLAN:			
		#BASIC PLAN --- PERCENTAGE COMPLETE VS PLANNED
		progress = calculate_progress_plan(num_completed, event_ids)
		logging.info("Today's Percentage Progress for {} is {}".format(user, progress))
			
		# Send progress to Fitbit
		step_count = fitbit.update_progress_decimal(user, progress, session)
		logging.info("Just added {} steps to {}'s account!".format(step_count, user.username))
		
		#update percentage for today
		save_today(user, num_completed, progress, session)
		
	elif user.metaphor == WEIGHT:		
		#WEIGHTED PROGRESS
		progress = calculate_progress_weight(event_ids, session)
		logging.info("Today's Weighted Progress for {} is {}".format(user, progress))
		
		# Send progress to Fitbit
		#step_count = fitbit.update_progress_decimal(user, progress, session)
		logging.info("Just added {} steps to {}'s account!".format(step_count, user.username))
		
		#update percentage for today
		save_today(user, num_completed, progress, session)		
					
	elif user.metaphor == TALLY:
		# TALLY - BASIC COUNT	
		progress = calculate_progress_tally(num_completed, event_ids)
		logging.info("Today's TALLY Progress for {} is {}".format(user, progress))
			
		# Send progress to Fitbit
		today = user.thisday()
		new_step_count = progress - today.computed_progress
		step_count = fitbit.update_progress_count(user, new_step_count, session)
		logging.info("Just added {} steps to {}'s account!".format(step_count, user.username))
		
		#update step count for today ( one LED per activitiy)
		save_today(user, num_completed, step_count, session)				
			
	elif user.metaphor == CHARGE:
		# CHARGE - WEIGHTED COUNT
		today = user.thisday()
		logging.debug("User {} prior count: {}, now completed {}".format(user.username, today.complete_count, num_completed ))
		if today.complete_count < num_completed:
			progress = calculate_progress_charge(num_completed, event_ids, session) 
			progress_change = progress - today.computed_progress
			logging.info("Today's CHARGE Progress update for {} is {}".format(user, progress_change))
			
			# Send progress change to Fitbit
			#step_count = fitbit.update_progress_count(user, progress_change, session)
			step_count = progress
			logging.info("Just added {} steps to {}'s account!".format(step_count, user.username))

			#update step count for today ( weighted*.10 per activity)
			save_today(user, num_completed, step_count, session)
		else:
			step_count = fitbit.get_dashboard_state(user)
			progress = user.thisday().computed_progress
	return progress, step_count

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
	max_steps = 100000
	activity_value = max_steps / 4 # number of LED's visible
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


def create_today(user, checkin_count, today_progress, session):
	'''
	on FIRST Poll, create a new DAY for the user, save the calculated checkin count and progress 
	'''
	thisDay = user.thisday() #prevent duplicates
	if thisDay is None:
		thisDay = Day(user_id=user.id, date=datetime.now().date(), computed_progress=today_progress, complete_count=checkin_count)	
		session.add(thisDay)
		session.commit()
	else:
		thisDay.computed_progress = today_progress
		thisDay.complete_count = checkin_count
		
	#add day id to each event in DB for better searchability
	today_events = weconnect.get_events_for_user(user, session)
	for ev in today_events:
		ev.day_id = thisDay.id

	logging.info("Creating this day: {}".format(thisDay))	
	try:		
		session.commit()
	except:
		session.rollback()
	
def save_today(user, checkin_count, today_progress, session):
	'''
	on Poll, save the calculated checkin count and progress 
	'''
	thisDay = user.thisday()
	#only update if there has been a change
	if thisDay.complete_count < checkin_count:	
		thisDay.computed_progress = today_progress 
		thisDay.complete_count = checkin_count
	session.commit()


def printout(user, timestamp):
	# timestamp, username, metaphor, day.complete_count, day.computed_progress, list of activities and weights, 
	logging.debug("printing...")
	file_dict = {}
	file_dict["timestamp"] = timestamp
	file_dict["user"] = user.username
	file_dict["metaphor"] = user.metaphor
	
	day = user.thisday()
	file_dict["checkins"] = day.complete_count
	file_dict["computed_progress"] = day.computed_progress
	
	act_list = []
	activities = user.activities.all()
	for a in activities:
		act = (a.name, a.weight)
		act_list.append(act)
	file_dict["activities"] = act_list
	with open("log.csv", "a", newline='') as file:
		fieldnames = file_dict.keys()
		writer = csv.DictWriter(file, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
		writer.writerow(file_dict)
		

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

