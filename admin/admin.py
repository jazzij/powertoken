import math
import dbmanager
from ptmodels import PtLog, PtUser

class Admin:
	pt_users = {}

	def __init__(self):
		rows = dbmanager.get_users()
		for row in rows:
			self._track_user(row)

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
		Return the latest progress for the user.
		"""
		logs = dbmanager.get_logs(user_id)
		last_index = len(logs) - 1
		last_log = logs[last_index]
		return math.floor(last_log["wc_progress"] * 100)

	def _track_user(self, row):
		wc_login_status = "Current" if (row["wc_id"] and row["wc_token"]) else "Expired"
		fb_login_status = "Current" if row["fb_token"] else "Expired"
		last_daily_progress = self._get_last_progress(row["id"])
		last_weekly_progress = self._compute_weekly_progress(row["id"])
		self.pt_users[row["id"]] = PtUser(row, fb, wc)