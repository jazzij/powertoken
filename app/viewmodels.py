"""
Contains the view models to be used with the admin dashboard.\n
Created by Abigail Franz on 3/19/2018.\n
"""

from datetime import datetime
from app.models import Log, User

class UserViewModel:
	def __init__(self, user):
		"""
		Param user is of type app.models.User
		"""
		self.id = user.id
		self.username = user.username
		self.registered_on = user.registered_on.strftime("%Y-%m-%d %I:%M %p")
		self.goal_period = user.goal_period
		self.wc_id = user.wc_id
		self.wc_status = "Current" if user.wc_id and user.wc_token else "Expired"
		self.fb_status = "Current" if user.fb_token else "Expired"
		self.daily_progress, self.weekly_progress = self.__last_progress__(user)

	def __last_progress__(self, user):
		logs = user.logs.all()
		last_log = logs[-1] if len(logs) > 0 else \
			Log(daily_progress=0, weekly_progress=0, step_count=0, user=user)
		return last_log.daily_progress * 100, last_log.weekly_progress * 100

	def __repr__(self):
		return "<UserViewModel {}>".format(self.username)

class LogViewModel:
	def __init__(self, log):
		"""
		Param log is of type app.models.Log
		"""
		self.id = log.id
		self.username = log.user.username
		self.timestamp = log.timestamp.strftime("%Y-%m-%d %I:%M %p")
		self.daily_progress = log.daily_progress * 100
		self.weekly_progress = log.weekly_progress * 100
		self.step_count = log.step_count

	def __repr__(self):
		return "<LogViewModel {} at {}>".format(self.username, self.timestamp)