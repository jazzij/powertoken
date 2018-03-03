"""
module powertoken\n
Contains the functionality for interfacing between WEconnect and Fitbit.\n
Created by Abigail Franz on 2/20/2018\n
Last modified by Abigail Franz on 2/21/2018
"""

import time
import dbmanager
import weconnect, fitbit

class PtUser:
	def __init__(self, row, fb, wc):
		self.row = row
		self.fb = fb
		self.wc = wc
		self.last_progress = 0

class PowerToken:
	"""
	Main class of the PowerToken background application.
	Runs every fifteen minutes (Cron job). Gets list of activities from the
	database, sorts it by time. If any start or end within the next fifteen
	minutes, add that user to a list. Then poll all the users in the list for
	progress.
	"""
	STEP_GOAL = 1000000
	pt_users = []

	def __init__(self):
		user_ids = dbmanager.get_users_with_current_activities()
		for user_id in user_ids:
			user = dbmanager.get_user(id=user_id)
			self.pt_users.push(user)

	def run_old(self):
		"""
		This code will run forever.
		"""
		while True:
			rows = dbmanager.get_users()
			if len(rows) != len(self.pt_users):
				for row in rows:
					if not self._is_tracked(row):
						self._track_user(row)

			for id in self.pt_users:
				self._poll_and_update(id)

	def run(self):
		"""
		This code will run forever.
		"""
		while True:
			rows = dbmanager.get_users()
			for row in rows:
				if not self._is_tracked(row):
					self._track_user(row)

			for id in self.pt_users:
				self._poll_and_update(id)

	def _poll_and_update(self, id):
		# Polls WEconnect for changes and then updates Fitbit. Progress will be a 
		# decimal percentage.
		daily_progress, weekly_progress = self.pt_users[id].wc.poll()
		progress = 0
		if self.pt_users[id].row["goal_period"] == "daily":
			progress = daily_progress
		else:
			progress = weekly_progress

		# Makes sure the poll request succeeded
		if progress != -1 and progress != self.pt_users[id].last_progress:
			step_count = self.pt_users[id].fb.reset_and_update(progress)
			dbmanager.insert_log(id, daily_progress, weekly_progress, step_count)
			self.pt_users[id].last_progress = progress

		time.sleep(60)