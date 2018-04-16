"""
This class contains the API calls to Fitbit (except for the login).\n
Created by Abigail Franz.\n
Last modified by Abigail Franz on 4/13/2018.
"""

import datetime, json, logging, requests
from common import is_valid, logfile
from models import Error

# Configures logging for the module
logger = logging.getLogger("background.fitbit")
logger.setLevel(logging.WARNING)
logpath = "data/background.fitbit.log"
handler = logging.FileHandler(logpath)
handler.setLevel(logging.WARNING)
formatter = logging.Formatter("%(asctime)s: %(levelname)-4s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class Fitbit:
	"""
	Class encapsulating the Fitbit API calls.
	"""
	base_url = 'https://api.fitbit.com/1/user/-'

	def __init__(self, user, session):
		self._user = user
		self._session = session
		self._auth_headers = {'Authorization': 'Bearer ' + user.fb_token}

	def change_step_goal(self, new_step_goal):
		"""
		Change the step goal to new_step_goal and return a Boolean indicating
		success.
		"""
		url = "{}/activities/goals/{}.json".format(self.base_url,
				self._user.goal_period)
		params = {
			"period" : self._user.goal_period,
			"type" : "steps",
			"value" : new_step_goal
		}
		response = requests.post(url, headers=self._auth_headers, params=params)
		if is_valid(response):
			new_goal = response.json()["goals"]["steps"]
			return True
		else:
			error = Error(
				summary = "Couldn't change the step goal.",
				origin = "background/fitbit.py, in _change_step_goals",
				message = response.json()["errors"][0]["message"],
				user = self._user
			)
			self._session.add(error)
			self._session.commit()
			logger.error("Couldn't change the step goal.")
			return False

	def update(self, percent):
		"""
		Given a percentage (from WEconnect), update the progress towards the
		step goal.
		"""
		prev_steps = self._get_current_steps()
		new_steps = int(percent * self._get_step_goal())
		success = self._log_step_activity(new_steps)
		if success:
			return new_steps
		else:
			logger.error("Couldn't update Fitbit")
			return None

	def reset_and_update(self, percent):
		"""
		Reset Fitbit to receive new step activities and return the number of
		steps added.
		"""
		# Deletes all Fitbit step activities for the day
		daily_activities = self._get_daily_step_activities()
		for activity in daily_activities:
			self._delete_activity(activity["logId"])

		# Updates Fitbit with the new percentage
		return self.update(percent)

	def _get_daily_step_activities(self):
		"""
		Return a list of all the activities the user has completed today. If
		the request is unsuccessful, return an empty list.
		"""
		current_date = self._get_current_date()
		url = "{}/activities/date/{}.json".format(self.base_url, current_date)
		response = requests.get(url, headers=self._auth_headers)
		if is_valid(response):
			return response.json()["activities"]
		else:
			error = Error(
				summary = "Couldn't get today's step activities.",
				origin = "background/fitbit.py, in _get_daily_step_activities",
				message = response.json()["errors"][0]["message"],
				user = self._user
			)
			self._session.add(error)
			self._session.commit()
			logger.error("Couldn't get today's step activities")
			return []

	# Helper - returns a list of all the activities the user has completed this
	# week. If the request is unsuccessful, returns an empty list
	def _get_weekly_step_activities(self):
		"""
		Return a list of all the activities the user has completed this week.
		If the request is unsuccessful, return an empty list.
		"""
		sunday = self._get_sunday()
		current_date = self._get_current_date()
		url = "{}/activities/steps/date/{}/{}.json".format(self.base_url,
				sunday, current_date)
		response = requests.get(url, headers=self._auth_headers)
		if is_valid(response):
			return response.json()["activities-log-steps"]
		else:
			error = Error(
				summary = "Couldn't get this week's step activities.",
				origin = "background/fitbit.py, in _get_weekly_step_activities",
				message = response.json()["errors"][0]["message"],
				user = self._user
			)
			self._session.add(error)
			self._session.commit()
			logger.error("Couldn't get this week's step activities")
			return []

	def _delete_activity(self, log_id):
		"""
		Delete an activity and return a Boolean indicating success.
		"""
		url = "{}/activities/{}.json".format(self.base_url, str(log_id))
		response = requests.delete(url, headers=self._auth_headers)
		if response.status_code == 204:
			return True
		else:
			error = Error(
				summary = "Activity {} was not successfully deleted".format(log_id),
				origin = "background/fitbit.py, in _delete_activity",
				message = response.json()["errors"][0]["message"],
				user = self._user
			)
			self._session.add(error)
			self._session.commit()
			logger.error("Activity {} was not successfully deleted.".format(log_id))
			return False

	def _get_step_goal(self):
		"""
		Get the user's step goal. If the request is unsuccessful, return a
		default value of 1 million.
		"""
		url = "{}/activities/goals/{}.json".format(self.base_url, 
				self._user.goal_period)
		response = requests.get(url, headers=self._auth_headers)
		if is_valid(response):
			return response.json()["goals"]["steps"]
		else:
			error = Error(
				summary = "Couldn't get step goal. Using 1,000,000 as default.",
				origin = "background/fitbit.py, in _get_step_goal",
				message = response.json()["errors"][0]["message"],
				user = self._user
			)
			self._session.add(error)
			self._session.commit()
			logger.warning("Couldn't get step goal. Using 1000000 as default.")
			return 1000000

	def _get_current_steps(self):
		"""
		Get today's current step count. If the request is unsuccessful, return
		None.
		"""
		date = self._get_current_date()
		url = "{}/activities/date/{}.json".format(self.base_url, date)
		response = requests.get(url, headers=self._auth_headers)
		if is_valid(response):
			return response.json()["summary"]["steps"]
		else:
			error = Error(
				summary = "Couldn't get today's step count.",
				origin = "background/fitbit.py, in _get_current_steps",
				message = response.json()["errors"][0]["message"],
				user = self._user
			)
			self._session.add(error)
			self._session.commit()
			logger.error("Couldn't get today's step count")
			return None
		
	def _log_step_activity(self, new_step_count):
		"""
		Log a walking activity containing the number of steps specified in
		new_step_count. Return a Boolean indicating success.
		"""
		url = "{}/activities.json".format(self.base_url)
		params = {
			"activityId" : '90013',
			"startTime" : self._get_current_time(),
			"durationMillis" : 3600000,
			"date" : self._get_current_date(),
			"distance" : new_step_count,
			"distanceUnit" : "steps"
		}
		response = requests.post(url, headers=self._auth_headers, params=params)
		if is_valid(response):
			return True
		else:
			error = Error(
				summary = "Couldn't log step activity.",
				origin = "background/fitbit.py, in _log_step_activity",
				message = response.json()["errors"][0]["message"],
				user = self._user
			)
			self._session.add(error)
			self._session.commit()
			logger.error("Couldn't log step activity")
			return False

	def _get_current_date(self):
		"""
		Return current date as a string in YYYY-MM-dd format.
		"""
		now = datetime.datetime.now()
		date_str = format("%d-%02d-%02d" % (now.year, now.month, now.day))
		return date_str

	def _get_current_time(self):
		"""
		Return current time as a string in HH:mm:ss format.
		"""
		now = datetime.datetime.now()
		time_str = format("%02d:%02d:%02d" % (now.hour, now.minute, now.second))
		return time_str

	def _get_sunday(self):
		"""
		Return the past Sunday in YYYY-MM-dd format.
		"""
		today = datetime.date.today()
		today_weekday = (today.weekday() + 1) % 7
		sun = today - datetime.timedelta(today_weekday)
		sun_str = format("%d-%02d-%02d" % (sun.year, sun.month, sun.day))
		return sun_str
