"""
module powertoken\n
Contains the functionality for interfacing between WEconnect and Fitbit.\n
Created by Abigail Franz on 2/20/2018\n
Last modified by Abigail Franz on 2/21/2018
"""

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
	"""
	STEP_GOAL = 1000000
	pt_users = {}

	def __init__(self):
		rows = dbmanager.get_users()
		for row in rows:
			self._track_user(row)

	def _track_user(self, row):
		# Doesn't add the user if any fields are missing
		if not (row["id"] and row["username"] and row["registered_on"]
				and row["goal_period"] and row["wc_id"] and row["wc_token"]
				and row["fb_token"]):
			return

		fb = fitbit.Fitbit(row["fb_token"], row["goal_period"])
		wc = weconnect.WeConnect(row["wc_id"], row["wc_token"],
				row["goal_period"])
		fb.change_step_goal(self.STEP_GOAL)
		self.pt_users[row["id"]] = PtUser(row, fb, wc)

	# user is a Row object from the database
	def _is_tracked_old(self, user):
		results = [u for u in self.pt_users if u.row == user]
		if len(results) > 0:
			return True
		else:
			return False

	# User is represented as a Row object from the database
	def _is_tracked(self, row):
		return row["id"] in self.pt_users:

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

			for user in self.pt_users:
				self._poll_and_update(user)

	def run(self):
		"""
		This code will run forever.
		"""
		while True:
			rows = dbmanager.get_users()
			for row in rows:
				if not self._is_tracked(row):
					self._track_user(row)

			for user in self.pt_users:
				self._poll_and_update(user)

	def _poll_and_update(self, user):
		# Polls WEconnect for changes and then updates Fitbit. Progress will be a 
		# decimal percentage.
		progress = user.wc.poll()
		print(progress)

		# Makes sure the poll request succeeded
		if progress != -1 and progress != user.last_progress:
			step_count = user.fb.reset_and_update(progress)
			dbmanager.insert_log(user.row["id"], progress, step_count)
			user.last_progress = progress