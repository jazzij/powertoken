from log_manager import get_logs
from ptmodels import PtLog, PtUser

class DbManager:
	def __init__(self):
		self._users = PtUser[]
		self._logs = PtLog[]

	def load_logs(self, username=None, user_id=None):
		logs_raw = get_logs(username=username, user_id=user_id)
		for log in logs_raw:
			self._logs.append(PtUser(log[0], log[1], log[2], log[3], log[4]))
		return self._logs