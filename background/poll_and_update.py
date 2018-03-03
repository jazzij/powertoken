"""
module poll_and_update
Script that runs the main PowerToken function: poll WEconnect and update Fitbit.
Meant to be run in CronTab, probably every 15 minutes.
Created by Abigail Franz on 2/28/2018
"""

import logging
import dbmanager
from weconnect import WeConnect
from fitbit import Fitbit

# Configures logging for the module
logger = logging.getLogger("background.poll_and_update")
logger.setLevel(logging.INFO)
logpath = "/export/scratch/powertoken/ptdata/background.poll_and_update.log"
handler = logging.FileHandler(logpath)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def poll_and_update():
	"""
	If any activities start or end within the next 15 minutes, add the user who 
	owns them to a list. Then poll all the users in the list for progress.
	"""
	user_ids = dbmanager.get_users_with_current_activities()
	if user_ids == None:
		logger.info("No current activities. Returning.")
		return
	for id in user_ids:
		user = dbmanager.get_user(id=id)
		wc = WeConnect(user["wc_id"], user["wc_token"], user["goal_period"])
		fb = Fitbit(user["fb_token"], user["goal_period"])
		
		# Gets progress (as a decimal percentage) from WEconnect.
		progress = 0
		daily_progress, weekly_progress = wc.poll()
		if user["goal_period"] == "daily":
			progress = daily_progress
		else:
			progress = weekly_progress

		# If the poll request succeeded, updates Fitbit and adds a new entry to
		# the logs.
		if progress == -1:
			logger.error("Couldn't get progress for user with id %d", id)
		elif progress == 0:
			logger.error("User with id %d has no progress yet today", id)
		else:
			step_count = fb.reset_and_update(progress)
			if step_count == -1:
				logger.error("Couldn't update Fitbit for user with id %d", id)
			else:
				dbmanager.insert_log(id, daily_progress, weekly_progress, step_count)

if __name__ == "__main__":
	logger.info("Starting the poll-and-update loop...")
	poll_and_update()
	logger.info("...Finished the poll-and-update loop.")