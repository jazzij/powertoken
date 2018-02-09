# fitbit.py
# This class contains the API calls to Fitbit (except for the login).
# Created by Abigail Franz
# Last modified by Abigail Franz on 1/29/2018

import datetime, json, logging, requests

class Fitbit:
	base_url = 'https://api.fitbit.com/1/user/-'
	_auth_headers = {}
	_goal_period = ""

	def __init__(self, fb_token, goal_period):
		self._auth_headers = {'Authorization': 'Bearer ' + fb_token}
		self._goal_period = goal_period
		#logging.basicConfig(filename="logs/powertoken.log", level=logging.INFO)

	# Changes the daily step goal to new_step_goal and returns True if successful
	def change_step_goal(self, new_step_goal):
		url = format("%s/activities/goals/%s.json" % (self.base_url, self._goal_period))
		params = {
			"period" : self._goal_period,
			"type" : "steps",
			"value" : new_step_goal
		}
		response = requests.post(url, headers=self._auth_headers, params=params)
		if self._is_valid(response):
			new_goal = response.json()["goals"]["steps"]
			#outputLogger.info(format(" Changed the %s step goal to %d" % (self._goal_period, newGoal)))
			return True
		else:
			return False

	# Given a percentage increase (from WEconnect), updates the progress
	# towards the step goal
	def update(self, percent):
		prev_steps = self._get_current_steps()
		new_steps = int(percent * self._get_step_goal())
		success = self._log_step_activity(new_steps)
		if success:
			return new_steps
		else:
			return -1

	# Resets Fitbit to receive new step activities and returns the number of steps
	# added.
	def reset_and_update(self, percent):
		# Deletes all Fitbit step activities for the day
		daily_activities = self._get_daily_step_activities()
		for activity in daily_activities:
			self._delete_activity(activity["logId"])

		# Updates Fitbit with the new percentage
		return self.update(percent)

	# Helper - returns a list of all the activities the user has completed today
	# If the request is unsuccessful, returns an empty list
	def _get_daily_step_activities(self):
		current_date = self._get_current_date()
		url = format("%s/activities/date/%s.json" % (self.base_url, current_date))
		response = requests.get(url, headers=self._auth_headers)
		if self._is_valid(response):
			return response.json()["activities"]
		else:
			return []

	# Helper - returns a list of all the activities the user has completed this
	# week. If the request is unsuccessful, returns an empty list
	def _get_weekly_step_activities(self):
		sunday = self._get_sunday()
		current_date = self._get_current_date()
		url = format("%s/activities/steps/date/%s/%s.json" 
					% (self.base_url, sunday, current_date))
		response = requests.get(url, headers=self._auth_headers)
		if self._is_valid(response):
			return response.json()["activities-log-steps"]
		else:
			return []

	# Helper - deletes an activity and returns True if successful
	def _delete_activity(self, logId):
		url = format("%s/activities/%s.json" % (self.base_url, str(logId)))
		response = requests.delete(url, headers=self._auth_headers)
		if response.status_code == 204:
			return True
		else:
			logging.error(format(" Activity %d was not successfully deleted." % (logId,)))
			return False

	# Helper - gets the user's step goal. If the request is unsuccessful,
	# returns a default value of 1 million.
	def _get_step_goal(self):
		goal_summary_url =  format("activities/goals/%s.json" % (self._goal_period,))
		url_str = self.base_url + goal_summary_url
		response = requests.get(url_str, headers=self._auth_headers)
		if self._is_valid(response):
			return response.json()["goals"]["steps"]
		else:
			return 1000000

	# Helper - gets today's current step count. If the request is unsuccessful,
	# returns -1.
	def _get_current_steps(self): 
		date = self._get_current_date()
		url = format("%s/activities/date/%s.json" % (self.base_url, date))
		response = requests.get(url, headers=self._auth_headers)
		if self._is_valid(response):
			return response.json()["summary"]["steps"]
		else:
			return -1
		
	# Helper - logs an activity containing the number of steps specified in 
	# newStepCount, and returns True if successful
	def _log_step_activity(self, new_step_count):
		url = format("%s/activities.json" % (self.base_url,))
		params = {
			"activityId" : '90013', # Walking (activityId=90013)
			"startTime" : self._get_current_time(), # HH:mm:ss
			"durationMillis" : 3600000, # 3,600,000 ms = 1 hr
			"date" : self._get_current_date(), # YYYY-MM-dd
			"distance" : new_step_count,
			"distanceUnit" : "steps"
		}
		response = requests.post(url, headers=self._auth_headers, params=params)
		if self._is_valid(response):
			logged_activity = response.json()
			return True
		else:
			return False

	# Helper - returns current date as a string in YYYY-MM-dd format
	def _get_current_date(self):
		now = datetime.datetime.now()
		date_str = format("%d-%02d-%02d" % (now.year, now.month, now.day))
		return date_str

	# Helper - returns current time as a string in HH:mm:ss format
	def _get_current_time(self):
		now = datetime.datetime.now()
		time_str = format("%02d:%02d:%02d" % (now.hour, now.minute, now.second))
		return time_str

	# Helper - returns the past Sunday in YYYY-MM-dd format
	def _get_sunday(self):
		today = datetime.date.today()
		today_weekday = (today.weekday() + 1) % 7	# SUN = 0, MON = 1, ... , SAT = 6
		sun = today - datetime.timedelta(today_weekday)
		sun_str = format("%d-%02d-%02d" % (sun.year, sun.month, sun.day))
		return sun_str

	# Helper - makes sure HTTP requests are successful
	def _is_valid(self, response):
		if response.status_code >= 300:
			#systemLogger.error(format(" Request could not be completed. Error: %d %s" 
			#		% (response.status_code, response.text)))
			return False
		else:
			return True
