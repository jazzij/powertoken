"""
Script that makes sure the database is up-to-date.\n
Meant to be run as a job in Crontab.\n
Created by Abigail Franz on 2/28/2018.\n
Modified by Abigail Franz on 3/15/2018.
"""

import logging
from datetime import datetime
import weconnect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Log, Activity

"""Format for datetimes received from WEconnect"""
WC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# Configures logging for the module
logger = logging.getLogger("background.hourly_maintenance")
logger.setLevel(logging.INFO)
logpath = "/export/scratch/powertoken/data/background.hourly_maintenance.log"
handler = logging.FileHandler(logpath)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: %(levelname)-4s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Sets up the SQLAlchemy engine and connects it to the Sqlite database pt.db 
engine = create_engine("sqlite:///../data/pt.db")
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
		expiration = datetime.strptime(act.expiration, "%Y-%m-%d %H:%M:%S")
		if expiration <= now:
			session.delete(act)
			session.commit()

	# Adds new activities
	added_count = 0
	for user in users:
		wc_acts = weconnect.get_activities(user["wc_id"], user["wc_token"])
		for act in wc_acts:
			was_added = add_or_update_activity(act, user)
			if was_added:
				added_count = added_count + 1
	logger.info("\t\t%d activities added to the database.", added_count)

	logger.info("\t...Done.")

def add_or_update_activity(activity, user):
	"""
	Insert new activity row into the database if it doesn't already exist and
	is not expired. If it exists but has been updated, update it in the
	database. Param "activity" is JSON object returned from WEconnect API
	endpoint. Return True if activity was inserted or updated and False if it 
	was not.
	"""
	# Determines the start and end times and expiration date (if any)
	st, et, expiration = extract_params(activity)
	act_id = activity["activityId"]

	# Boolean indicating whether or not the activity was inserted/updated
	status = False

	# Ignores the activity if it's already expired
	if expiration <= datetime.now():
		status = False
	else:
		# If the activity already exists in the database, sees if it's been
		# modified recently. If yes, updates it. If not, ignores it.
		existing = session.query("Activity").filter(Activity.activity_id == act_id)
		if existing:
			modified = datetime.strptime(activity["dateModified"], WC_FORMAT)
			if modified >= datetime.now() - timedelta(days=1):
				existing = Activity(activity_id=act_id, start_time=st,
					end_time=et, expiration=expiration, user=user)
				session.commit()
				status = True
			else:
				status = False
		else:
			# If the activity doesn't exist in the database, adds it.
			new = Activity(activity_id=act_id, start_time=st, end_time=et,
				expiration=expiration, user=user)
			session.add(new)
			session.commit()
			status = True

	return status

def extract_params(activity):
	"""
	Given a JSON activity object from WEconnect, extract the important
	parameters (start time, end time, and expiration date).
	"""
	# Determines the start and end times
	ts = datetime.strptime(activity["dateStart"], WC_FORMAT)
	te = ts + timedelta(minutes=activity["duration"])

	# Determines the expiration date (if any)
	expiration = datetime(MAXYEAR, 12, 31)
	if activity["repeat"] == "never":
		expiration = te
	if activity["repeatEnd"] != None:
		expiration = datetime.strptime(activity["repeatEnd"], WC_FORMAT)

	return ts, te, expiration

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
