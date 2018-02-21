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

class PowerToken:
	"""
	Main class of the PowerToken background application.
	"""
	STEP_GOAL = 1000000
	pt_users = []

	def __init__(self):
		pt_users = dbmanager.get_users()
		for user in pt_users:
			self._add_user(user)

	def _track_user(self, user):
		fb = fitbit.Fitbit(user["fb_token"], user["goal_period"])
		wc = weconnect.WeConnect(user["wc_id"], user["wc_token"],
				user["goal_period"])
		fb.change_step_goal(self.STEP_GOAL)
		self.pt_users.append(PtUser(user, fb, wc))

	# user is a Row object from the database
	def _is_tracked(self, user):
		results = [u for u in self.pt_users if u.row == user]
		if len(results) > 0:
			return True
		else:
			return False

	def run():
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

	def _poll_and_update(self, user):
		# Polls WEconnect for changes and then updates Fitbit. Progress will be a 
		# decimal percentage.
		progress = wc.poll()
		print(progress)

		# Makes sure the poll request succeeded
		if progress != -1:
			step_count = fb.reset_and_update(progress)
			dbmanager.insert_log(user.row["id"], progress, step_count)