"""
Script that makes sure the database is up-to-date.\n
Meant to be run as a job in Crontab.\n
Created by Abigail Franz on 2/28/2018.\n
Modified by Abigail Franz on 3/15/2018.
"""

import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from weconnect import get_activities
from models import Base, User, Log, Activity, DB_PATH
from helpers import add_or_update_activity

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
	for user in users:
		if not all([user.username, user.wc_id, user.wc_token, user.fb_token]):
			session.delete(user)
			session.commit()

	# Makes sure all access tokens are current
	users = session.query(User).all()
	for user in users:
		# Determine if WC token is expired
		# Determine if FB token is expired
		logger.warning("\t\tToken expiration check not implemented.")

	logger.info("\t...Done.")

def maintain_activities():
	"""
	Go through the activities table of the database and check 3 things:
	1. No activity is assigned to a user that no longer exists in the database.
	2. All activities are unexpired, and expired activities are removed.
	3. If users have added/updated activities, those are added to the database.
	"""
	logger.info("\tRunning activity maintenance...")

	# Makes sure activities aren't assigned to "ghost users"
	activities = session.query(Activity).all()
	users = session.query(User).all()
	for act in activities:
		if not act.user in users:
			session.delete(act)
			session.commit()

	# Makes sure no activities are expired
	activities = session.query(Activity).all()
	now = datetime.now()
	for act in activities:
		if act.expiration <= now:
			session.delete(act)
			session.commit()

	# Adds new activities
	added_count = 0
	for user in users:
		wc_acts = get_activities(user.wc_id, user.wc_token)
		for act in wc_acts:
			print(act)
			was_added = add_or_update_activity(session, act, user)
			print("Was it added? {}".format("Yes" if was_added else "No"))
			if was_added:
				added_count = added_count + 1
	logger.info("\t\t%d activities added to the database.", added_count)

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
	maintain_admins()
	logger.info("...Done.")
