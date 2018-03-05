"""
module ptadmin\n
Main class of the PowerToken/Admin Flask application\n
Last modified by Abigail Franz on 3/5/2018
"""

import math
import dbmanager

class PtUser:
	"""
	Object to represent a user of the PowerToken system.
	"""
	def __init__(self, row, wc_login_status, fb_login_status, daily_progress=0,
				weekly_progress=0):
		self.row = row
		self.wc_login_status = wc_login_status
		self.fb_login_status = fb_login_status
		self.daily_progress = daily_progress
		self.weekly_progress = weekly_progress

class PtLog:
	"""
	Object to represent a progress log.
	"""
	def __init__(self, row, username):
		self.row = row
		self.username = username

def load_users():
	pt_users_raw = dbmanager.get_users()
	pt_users = {}
	for row in pt_users_raw:
		wc_status = "Current" if (row["wc_id"] and row["wc_token"]) else "Expired"
		fb_status = "Current" if row["fb_token"] else "Expired"
		daily_progress, weekly_progress = self._get_last_progress(row["id"])
		user = PtUser(row, fb_status, wc_status, daily_progress, weekly_progress)
		pt_users[row["id"]] = user
	return pt_users

def load_logs():
	pt_logs_raw = dbmanager.get_logs()
	pt_logs = {}
	for row in pt_logs_raw:
		username = dbmanager.get_user(id=row["user_id"])["username"]
		log = PtLog(row, username)
		pt_logs[row["id"]] = log
	return pt_logs

def _get_last_progress(self, user_id):
	"""
	Return the latest progress (daily and weekly) for the user.
	"""
	logs = dbmanager.get_logs(user_id)
	last_index = len(logs) - 1
	if last_index < 0:
		return 0, 0
	last_log = logs[last_index]
	daily_progress = math.floor(last_log["daily_progress"] * 100)
	weekly_progress = math.floor(last_log["weekly_progress"] * 100)
	return daily_progress, weekly_progress

def _track_user(self, row):
	wc_status = "Current" if (row["wc_id"] and row["wc_token"]) else "Expired"
	fb_status = "Current" if row["fb_token"] else "Expired"
	daily_progress, weekly_progress = self._get_last_progress(row["id"])
	user = PtUser(row, fb_status, wc_status, daily_progress, weekly_progress)
	self.pt_users[row["id"]] = user

def _track_log(self, row):
	log = PtLog(
		row["id"],
		row["user_id"],
		self.pt_users[row["user_id"]].row["username"],
		row["timestamp"],
		row["daily_progress"],
		row["weekly_progress"],
		row["step_count"]
	)
	self.pt_logs[row["id"]] = log

class PtAdmin:
	"""
	Main class for the PowerToken/Admin application
	"""
	pt_users = {}
	pt_logs = {}

	def __init__(self):
		rows = dbmanager.get_users()
		for row in rows:
			self._track_user(row)
		logrows = dbmanager.get_logs()
		for logrow in logrows:
			self._track_log(logrow)

	def load_users():
		pt_users_raw = dbmanager.get_users()
		pt_users = []
		for u in pt_users_raw:
			user = PtUser(
				id=u["id"],
				username = u["username"],
				registered_on = u["registered_on"],
				goal_period = u["goal_period"],
				wc_login_status = "Current" if (u["wc_id"] and u["wc_token"]) else "Expired",
				fb_login_status = "Current" if u["fb_token"] else "Expired",
				wc_daily_progress = get_last_progress(u["id"])
			)
			pt_users.append(user)
		return pt_users

	def _get_last_progress(self, user_id):
		"""
		Return the latest progress (daily and weekly) for the user.
		"""
		logs = dbmanager.get_logs(user_id)
		last_index = len(logs) - 1
		if last_index < 0:
			return 0, 0
		last_log = logs[last_index]
		daily_progress = math.floor(last_log["daily_progress"] * 100)
		weekly_progress = math.floor(last_log["weekly_progress"] * 100)
		return daily_progress, weekly_progress

	def _track_user(self, row):
		wc_status = "Current" if (row["wc_id"] and row["wc_token"]) else "Expired"
		fb_status = "Current" if row["fb_token"] else "Expired"
		daily_progress, weekly_progress = self._get_last_progress(row["id"])
		user = PtUser(row, fb_status, wc_status, daily_progress, weekly_progress)
		self.pt_users[row["id"]] = user

	def _track_log(self, row):
		log = PtLog(
			row["id"],
			row["user_id"],
			self.pt_users[row["user_id"]].row["username"],
			row["timestamp"],
			row["daily_progress"],
			row["weekly_progress"],
			row["step_count"]
		)
		self.pt_logs[row["id"]] = log
