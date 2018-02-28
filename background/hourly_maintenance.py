"""
module hourly_maintenance\n
Script that makes sure the database is up-to-date.\n
Meant to be run as a job in CronTab.\n
Created by Abigail Franz on 2/28/2018\n
"""

from datetime import datetime
import dbmanager
import weconnect

# Global list to hold errors encountered during maintenance
errors = []

def maintain_users():
	"""
	Go through the users table of the database and check 2 things:
	1. All user fields are complete, and incomplete profiles are removed.
	2. All WEconnect and Fitbit access tokens are unexpired.
	"""
	print("Running user maintenance...")

	# Removes incomplete user rows from the database
	users = dbmanager.get_users()
	for user in users:
		if not(user["username"] and user["wc_id"] and user["wc_token"]
			and user["fb_token"]):
			dbmanager.delete_user(user["id"])

	# Makes sure all access tokens are current
	users = dbmanager.get_users()
	for user in users:
		# Determine if WC token is expired
		# Determine if FB token is expired
		x = 1 + 1

	print("Done.")

def maintain_activities():
	"""
	Go through the activities table of the database and check 2 things:
	1. No activity is assigned to a user that no longer exists in the database.
	2. All activities are unexpired, and expired activities are removed.
	3. If users have added new activities, those are added to the database.
	"""
	print("Running activity maintenance...")

	# Makes sure activities aren't assigned to "ghost users"
	activities = dbmanager.get_activities()
	user_ids = dbmanager.get_user_ids()
	for activity in activities:
		if not activity["user_id"] in user_ids:
			dbmanager.delete_activity(activity["id"])

	# Makes sure no activities are expired
	activities = dbmanager.get_activities()
	dt_format = "%Y-%m-%dT%H:%M:%S.%fZ"
	now = datetime.now()
	for activity in activities:
		expiration = datetime.strptime(activity["expiration"], dt_format)
		if expiration <= now:
			dbmanager.delete_activity(activity["id"])

	# Adds new activities
	users = dbmanager.get_users()
	added_count = 0
	for user in users:
		activities = weconnect.get_activities(user["wc_id"], user["wc_token"])
		for activity in activities:
			was_added = dbmanager.insert_activity(user["id"], activity)
			if was_added:
				added_count = added_count + 1
	print(format("%d activities added to the database" % (added_count,)))

	print("Done")

if __name__ == "__main__":
	maintain_users()
	maintain_activities()
	print("Finished database maintenance; no errors to report.")