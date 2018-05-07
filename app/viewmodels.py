"""
Contains the view models to be used with the admin dashboard.\n
Created by Abigail Franz on 3/19/2018.\n
"""

from datetime import datetime
from app.helpers import TODAY
from app.models import Day, Log, User

class UserViewModel:
	def __init__(self, user):
		"""
		:param app.models.User user
		"""
		self.id = user.id
		self.username = user.username
		self.registered_on = user.registered_on.strftime("%Y-%m-%d")
		self.wc_id = user.wc_id
		self.wc_status = "Current" if user.wc_id and user.wc_token else "Expired"
		self.fb_status = "Current" if user.fb_token else "Expired"
		self.last_check_in = self._last_check_in(user) 
		self.daily_progress, self.weekly_progress = self._todays_progress(user)

	def _last_check_in(self, user):
		days = user.days.filter(Day.computed_progress > 0).all()
		last_day = days[-1] if len(days) > 0 else None
		if last_day is None:
			return "Never"
		else:
			return last_day.date.strftime("%Y-%m-%d")

	def _todays_progress(self, user):
		day = user.days.filter(Day.date == TODAY).first()

		# If the user has no Day object for today, return 0
		if day is None:
			return 0.0, 0.0

		total_progress = day.computed_progress
		weekday = TODAY.weekday()
		for i in range(1, weekday):
			d = user.days.filter(Day.date == (day.date - timedelta(days=i))).first()
			total_progress += d.computed_progress
		weekly_avg = total_progress / (weekday + 1) if total_progress > 0 else 0

		return day.computed_progress * 100, weekly_avg * 100

	def __repr__(self):
		return "<UserViewModel {}>".format(self.username)

class LogViewModel:
	def __init__(self, log):
		"""
		:param app.models.Log log
		"""
		self.id = log.id
		self.username = log.user.username
		self.timestamp = log.timestamp.strftime("%Y-%m-%d %I:%M %p")
		self.daily_progress = log.daily_progress * 100
		self.weekly_progress = log.weekly_progress * 100
		self.step_count = log.step_count

	def __repr__(self):
		return "<LogViewModel {} at {}>".format(self.username, self.timestamp)