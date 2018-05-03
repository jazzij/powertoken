"""
Script that makes sure the database is up-to-date.\n
Meant to be run as a job in CronTab.\n
Created by Abigail Franz on 2/28/2018.\n
Last modified by Abigail Franz on 5/2/2018.
"""

from datetime import datetime
from db import session
import fitbit
from models import Activity, Day, Error, Event, User
from helpers import (add_or_update_activity, populate_todays_events, 
	check_users_complete, check_days)
import weconnect

def maintain_users():
	"""
	Go through the users table of the database and check 3 things:
	1. All user fields are complete and access tokens are unexpired.
	2. Every user has a Fitbit step goal of 1,000,000.
	3. Every user has at least 5 Days in the days table.
	"""
	check_users_complete()
	for user in users:
		fitbit.change_step_goal(user, 1000000)
		check_days(user)

def maintain_activities():
	"""
	Go through the activities table of the database and check 2 things:
	1. All activities are unexpired, and expired activities are removed.
	2. If users have added/updated activities, those are added to the database.
	"""
	# Makes sure no activities are expired
	activities = session.query(Activity).all()
	now = datetime.now()
	for act in activities:
		if act.expiration <= now:
			session.delete(act)
			session.commit()
			del_count += 1

	# Adds new activities
	added_count, updated_count = 0, 0
	for user in users:
		wc_acts = weconnect.get_activities(user)
		for act in wc_acts:
			add_or_update_activity(act, user)

def maintain_events():
	"""
	Populates (or updates) the list of today's events
	"""
	users = session.query(User).all()
	for user in users:
		populate_todays_events(user)

if __name__ == "__main__":
	maintain_users()
	maintain_activities()
	maintain_events()
