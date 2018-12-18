"""
Script that runs the main PowerToken function: poll WEconnect and update Fitbit.
Meant to be run in Crontab, probably every 5-15 minutes.\n
Created by Abigail Franz on 2/28/2018.\n
Last modified by Abigail Franz on 5/7/2018.
"""
from datetime import datetime
from db import session
from models import Activity, Event, Log, User
import fitbit
import weconnect
from helpers import compute_days_progress, compute_days_progress_tally
import logging, sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def poll_and_save():
	"""
	Check for new events each day and save them to the database
	TODO:First poll of the day adds new events
	TODO: Subsequent polls should update completion status
		id = db.Column(db.Integer, primary_key=True)
		eid = db.Column(db.String, index=True)
		start_time = db.Column(db.DateTime)	# Date portion is ignored
		end_time = db.Column(db.DateTime)	# Date portion is ignored
		completed = db.Column(db.Boolean)
		day_id = db.Column(db.Integer, db.ForeignKey("day.id"))
		activity_id = 
	"""
	users = User.query.all()
	for user in users:
		logging.debug("polling for {}".format(user))
		# API call to WEconnect activities-with-events
		activity_events = weconnect.get_todays_events(user)
		logging.debug(activity_events)	
	
	for activity in activity_events:
		for ev in activity["events"]:
			event = session.query(Event).filter_by(eid == ev["eid"]).first()
			if event:
				#update the completion
				event.completed = (ev["didCheckin"] == True)
			else: #eid doesn't exist, add new event
				newEvent = weconnect.createNewEvent(ev)
				session.add(newEvent)
	try:		
		session.commit()
		print("Received {} Activity events in last poll.").format(len(activity_events))
	except:
		session.rollback()
		print("Session Commit failed")

def poll_and_update():
	"""
	For each user in the database:
	1. Poll WEconnect to find out how many of the user''s events for today
	   have been completed.
	2. Compute the user's progress for today.
	2. If the user has made progress since the last time this script was run,
	   send the new progress to Fitbit as a walking activity with the following
	   number of steps: progress * 1,000,000.
	"""
	users = session.query(User).all()
	for user in users:
		logging.debug("polling for {}".format(user))
		# API call to WEconnect activities-with-events
		activity_events = weconnect.get_todays_events(user)
		logging.debug(activity_events)
		
		# Keep track in DB of which events have didCheckin set to True
		#for activity in activity_events:
		#	for ev in activity["events"]:
		#		if ev["didCheckin"]:
		#			event = session.query(Event).filter(Event.eid == ev["eid"]).first()
		#			event.completed = True
		#			print("{} completed".format(event))
		#session.commit()
'''
		# Compute progress with fade or tally algorithm
		thisday = user.thisday()
		print("User: {}, Day: {}".format(user, user.id))
		#progress = compute_days_progress(thisday) #FADE
		progress = compute_days_progress_tally(thisday) #TALLY 
		#progress = compute_days_progress_tally(activity_events) **BUG IS HERE
		
		
		print("Progress is {}".format(progress))
		if not thisday.computed_progress == progress:
			# Update today's Day object in the database
			thisday.computed_progress = progress
			session.commit()

			# Send progress to Fitbit
			step_count = fitbit.update_progress(user, progress)

			# Add a Log object to the database
			log = Log(wc_progress=progress, fb_step_count=step_count, user=user)
'''


if __name__ == "__main__":
	poll_and_save()