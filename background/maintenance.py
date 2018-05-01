"""
Script that makes sure the database is up-to-date.\n
Meant to be run as a job in CronTab.\n
Created by Abigail Franz on 2/28/2018.\n
Modified by Abigail Franz on 4/30/2018.
"""

import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import session
import fitbit
from models import Base, User, Log, Activity, Error, DB_PATH
from helpers import add_or_update_activity, populate_todays_events
import weconnect

# Configures logging for the module
logger = logging.getLogger("background.maintenance")
logger.setLevel(logging.INFO)
logpath = "data/background.maintenance.log"
handler = logging.FileHandler(logpath)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: %(levelname)-4s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def maintain_users():
	"""
	Go through the users table of the database and check 2 things:
	1. All user fields are complete, and incomplete profiles are removed.
	2. All WEconnect and Fitbit access tokens are unexpired.
	"""
	# Removes incomplete user rows from the database
	users = session.query(User).all()
	del_count = 0
	for user in users:
		if not all([user.username, user.wc_id, user.wc_token, user.fb_token]):
			session.delete(user)
	if del_count > 0:
		logger.info("%d incomplete users removed from the database", del_count)

	# TODO: Make sure all access tokens are current
	users = session.query(User).all()
	for user in users:
		#Determine if WC token is expired
		#Determine if FB token is expired
		pass

	for user in users:
		fitbit.change_step_goal(user, 1000000)

	session.commit()

def maintain_activities():
	"""
	Go through the activities table of the database and check 3 things:
	1. No activity is assigned to a user that no longer exists in the database.
	2. All activities are unexpired, and expired activities are removed.
	3. If users have added/updated activities, those are added to the database.
	"""
	del_count = 0

	# Makes sure activities aren't assigned to "ghost users"
	activities = session.query(Activity).all()
	users = session.query(User).all()
	for act in activities:
		if not act.user in users:
			session.delete(act)
			del_count += 1

	# Makes sure no activities are expired
	activities = session.query(Activity).all()
	now = datetime.now()
	for act in activities:
		if act.expiration <= now:
			session.delete(act)
			del_count += 1

	# Adds new activities
	added_count, updated_count = 0, 0
	for user in users:
		wc_acts = weconnect.get_activities(user)
		for act in wc_acts:
			status = add_or_update_activity(act, user)
			if status == "Inserted":
				added_count += 1
			elif status == "Updated":
				updated_count += 1
	
	session.commit()

	if del_count > 0:
		logger.info("%d activities removed from the database.", del_count)
	if added_count > 0:
		logger.info("%d activities added to the database.", added_count)
	if updated_count > 0:
		logger.info("%d activities updated in the database.", updated_count)

def maintain_events():
	"""
	Populates (or updates) the list of today's events
	"""
	users = session.query(User).all()
	for user in users:
		populate_todays_events(user)

def maintain_logs():
	"""
	Makes sure no logs are assigned to "ghost users"
	"""
	logs = session.query(Log).all()
	users = session.query(User).all()
	del_count = 0
	for log in logs:
		if not log.user in users:
			session.delete(log)
			session.commit()
			del_count += 1
	if del_count > 0:
		logger.info("%d logs removed from the database.", del_count)

if __name__ == "__main__":
	logger.info("Running database maintenance...")
	maintain_users()
	maintain_activities()
	maintain_logs()
	maintain_events()
	logger.info("...Done.")
