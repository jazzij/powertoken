"""
module hourly_maintenance\n
Script that makes sure the database is up-to-date.\n
Meant to be run as a job in Cron Tab.\n
Created by Abigail Franz on 2/28/2018\n
"""

import logging
from datetime import datetime
import weconnect

# Configures logging for the module
logger = logging.getLogger("background.hourly_maintenance")
logger.setLevel(logging.INFO)
logpath = "/export/scratch/powertoken/data/background.hourly_maintenance.log"
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
	logger.info("\tRunning user maintenance...")

	# Removes incomplete user rows from the database
	users = dbmanager.get_users()
	for user in users:
		if not(user["username"] and user["wc_id"] and user["wc_token"]
			and user["fb_token"]):
			success = dbmanager.delete_user(user["id"])
			if not success:
				logger.error("\t\tUnable to delete user with id %d.", user["id"])

	# Makes sure all access tokens are current
	users = dbmanager.get_users()
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

	# Just in case activities table has been deleted
	success = dbmanager.create_activities_if_dne()
	if not success:
		logger.error("\t\tUnable to determine if activities table exists.") 

	# Makes sure activities aren't assigned to "ghost users"
	activities = dbmanager.get_activities()
	user_ids = dbmanager.get_user_ids()
	for act in activities:
		if not act["user_id"] in user_ids:
			success = dbmanager.delete_activity(act["id"])
			if not success:
				logger.error("\t\tUnable to delete activity with id %d", act["id"])

	# Makes sure no activities are expired
	activities = dbmanager.get_activities()
	now = datetime.now()
	for act in activities:
		expiration = datetime.strptime(act["expiration"], "%Y-%m-%d %H:%M:%S")
		if expiration <= now:
			success = dbmanager.delete_activity(act["id"])
			if not success:
				logger.error("\t\tUnable to delete activity with id %d", act["id"])

	# Adds new activities
	users = dbmanager.get_users()
	added_count = 0
	for user in users:
		activities = weconnect.get_activities(user["wc_id"], user["wc_token"])
		for act in activities:
			was_added = dbmanager.insert_activity(user["id"], act)
			if was_added:
				added_count = added_count + 1
	logger.info("\t\t%d activities added to the database.", added_count)

	logger.info("\t...Done.")

def maintain_admins():
	"""
	Go through the admins table of the database and check 1 thing:
	"""
	logger.info("\tRunning admin maintenance...")

	# Just in case admins table has been deleted
	success = dbmanager.create_admins_if_dne()
	if not success:
		logger.error("\t\tUnable to determine if admins table exists.")
	
	logger.info("\t...Done.")

if __name__ == "__main__":
	logger.info("Running database maintenance...")
	maintain_users()
	maintain_activities()
	maintain_admins()
	logger.info("...Done.")
