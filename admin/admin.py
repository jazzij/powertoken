import math
import dbmanager
from ptmodels import PtLog, PtUser

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

def get_last_progress(user_id):
	"""
	Return the latest progress for the user.
	"""
	logs = dbmanager.get_logs(user_id)
	last_index = len(logs) - 1
	last_log = logs[last_index]
	return math.floor(last_log["wc_progress"] * 100)