"""
Script that makes sure the database is up-to-date.\n
Meant to be run as a job in CronTab.\n
Created by Abigail Franz on 2/28/2018.\n
Modified by Abigail Franz on 3/26/2018.
"""

import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Log, Activity, DB_PATH
from fitbit import Fitbit
from helpers import add_or_update_activity
from weconnect import get_activities

# Configures logging for the module
logger = logging.getLogger("background.maintenance")
logger.setLevel(logging.INFO)
logpath = "data/background.maintenance.log"
handler = logging.FileHandler(logpath)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: %(levelname)-4s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Sets up the SQLAlchemy engine and connects it to the Sqlite database.
engine = create_engine("sqlite:///" + DB_PATH)
Base.metadata.bind = engine
DbSession = sessionmaker(bind=engine)
session = DbSession()

def maintain_users():
	"""
	Go through the users table of the database and check 2 things:
	1. All user fields are complete, and incomplete profiles are removed.
	2. All WEconnect and Fitbit access tokens are unexpired.
	"""
	logger.info("\tRunning user maintenance...")

	# Removes incomplete user rows from the database
	users = session.query(User).all()
	del_count = 0
	for user in users:
		if not all([user.username, user.wc_id, user.wc_token, user.fb_token]):
			session.delete(user)
			session.commit()
	if del_count > 0:
		logger.info("\t\t%d incomplete users removed from the database", del_count)

	# TODO: Make sure all access tokens are current
	users = session.query(User).all()
	for user in users:
		#Determine if WC token is expired
		#Determine if FB token is expired
		pass
	logger.warning("\t\tToken expiration check not implemented.")

	for user in users:
		fb = Fitbit(user, session)
		fb.change_step_goal(1000000)

	logger.info("\t...Done.")

def maintain_activities():
	"""
	Go through the activities table of the database and check 3 things:
	1. No activity is assigned to a user that no longer exists in the database.
	2. All activities are unexpired, and expired activities are removed.
	3. If users have added/updated activities, those are added to the database.
	"""
	logger.info("\tRunning activity maintenance...")
	del_count = 0

	# Makes sure activities aren't assigned to "ghost users"
	activities = session.query(Activity).all()
	users = session.query(User).all()
	for act in activities:
		if not act.user in users:
			session.delete(act)
			session.commit()
			del_count += 1

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
		wc_acts = get_activities(user, session)
		for act in wc_acts:
			status = add_or_update_activity(session, act, user)
			if status == "Inserted":
				added_count += 1
			elif status == "Updated":
				updated_count += 1

	if del_count > 0:
		logger.info("\t\t%d activities removed from the database.", del_count)
	if added_count > 0:
		logger.info("\t\t%d activities added to the database.", added_count)
	if updated_count > 0:
		logger.info("\t\t%d activities updated in the database.", updated_count)

	logger.info("\t...Done.")

def maintain_logs():
	"""
	Makes sure no logs are assigned to "ghost users"
	"""
	logger.info("\tRunning log maintenance...")

	logs = session.query(Log).all()
	users = session.query(User).all()
	del_count = 0
	for log in logs:
		if not log.user in users:
			session.delete(log)
			session.commit()
			del_count += 1
	if del_count > 0:
		logger.info("\t\t%d logs removed from the database.", del_count)

	logger.info("\t...Done.")

def maintain_admins():
	"""
	Go through the admins table of the database and check 1 thing:
	"""
	logger.info("\tRunning admin maintenance...")

	logger.warning("\t\tNo maintenance set for admin table.")
	
	logger.info("\t...Done.")

if __name__ == "__main__":
	logger.info("Running database maintenance...")
	maintain_users()
	maintain_activities()
	maintain_logs()
	maintain_admins()
	logger.info("...Done.")
