"""
module poll_and_update
Script that runs the main PowerToken function: poll WEconnect and update Fitbit.
Meant to be run in CronTab, probably every 15 minutes.
Created by Abigail Franz on 2/28/2018
"""

import dbmanager
from weconnect import WeConnect
from fitbit import Fitbit

def poll_and_update():
	"""
	If any activities start or end within the next 15 minutes, add the user who 
	owns them to a list. Then poll all the users in the list for progress.
	"""
	user_ids = dbmanager.get_users_with_current_activities()
	if user_ids == None:
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
		if progress != -1:
			step_count = fb.reset_and_update(progress)
			dbmanager.insert_log(id, daily_progress, weekly_progress, step_count)

if __name__ == "__main__":
	poll_and_update()