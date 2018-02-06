from tinydb import TinyDB
from ptmodels import PtLog, PtUser

class DbManager:
	_logs_path = "data/logs.json"
	_users_path = "data/users.json"

	def __init__(self):
		self._logs_db = TinyDB(self._logs_path)
		self._users_db = TinyDB(self._users_path)

	def get_all_users(self):
		all_users = PtUser[]
		for user in self._users_db:
			username = user["username"]
			registered_on = user["registeredOn"]
			wc_login_status = "Current" if (user["wcUserId"] and user["wcAccessToken"]) else "Expired"
			fb_login_status = "Current" if user["fbAccessToken"] else "Expired"
			all_users.append(PtUser(username, registered_on, wc_login_status, fb_login_status))
		return all_users

	def get_all_logs(self):
		all_logs = PtLog[]
		for log in self._logs_db:
			username = log["username"]
			