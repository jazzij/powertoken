# fitbit.py
# This class contains the API calls to Fitbit (except for the login).
# Created by Abigail Franz
# Last modified by Abigail Franz on 1/29/2018

import datetime, json, logging, requests

class Fitbit:
	fbBaseUrl = 'https://api.fitbit.com/1/user/-/'
	_authHeaders = {}
	_goalPeriod = ""

	def __init__(self, fbAccessToken, goalPeriod):
		self._authHeaders = {'Authorization': 'Bearer ' + fbAccessToken}
		self._goalPeriod = goalPeriod
		#logging.basicConfig(filename="logs/powertoken.log", level=logging.INFO)

	# Changes the daily step goal to newStepGoal and returns True if successful
	def changeStepGoal(self, newStepGoal):
		goalUrl = format("activities/goals/%s.json" % (self._goalPeriod,))
		urlStr = self.fbBaseUrl + goalUrl
		params = {
			"period" : self._goalPeriod,
			"type" : "steps",
			"value" : newStepGoal
		}
		response = requests.post(urlStr, headers=self._authHeaders, params=params)
		if self._isValid(response):
			newGoal = response.json()["goals"]["steps"]
			outputLogger.info(format(" Changed the %s step goal to %d" % (self._goalPeriod, newGoal)))
			return True
		else:
			return False

	# Given a percentage increase (from WEconnect), updates the progress
	# towards the step goal
	def update(self, percent):
		prevSteps = self._getCurrentSteps()
		newSteps = int(percent * self._getStepGoal())
		logSuccessful = self._logStepActivity(newSteps)
		if logSuccessful:
			outputLogger.info(format(" Changed the step count from %d to %d" 
					% (prevSteps, newSteps)))
			return newSteps
		else:
			return -1

	# Resets Fitbit to receive new step activities and returns the number of steps
	# added.
	def resetAndUpdate(self, percent):
		# Deletes all Fitbit step activities for the day
		dailyActivities = self._getDailyStepActivities()
		for activity in dailyActivities:
			logId = activity["logId"]
			self._deleteActivity(logId)

		# Updates Fitbit with the new percentage
		return self.update(percent)

	# Helper - returns a list of all the activities the user has completed today
	# If the request is unsuccessful, returns an empty list
	def _getDailyStepActivities(self):
		activityListUrl = format("activities/date/%s.json" % (self._getCurrentDate(),))
		urlStr = self.fbBaseUrl + activityListUrl
		response = requests.get(urlStr, headers=self._authHeaders)
		if self._isValid(response):
			activityListJson = response.json()
			activityList = activityListJson["activities"]
			return activityList
		else:
			return []

	# Helper - returns a list of all the activities the user has completed this
	# week. If the request is unsuccessful, returns an empty list
	def _getWeeklyStepActivities(self):
		activityListUrl = format("activities/steps/date/%s/%s.json" 
				% (self._getSunday(), self._getCurrentDate()))
		urlStr = self.fbBaseUrl + activityListUrl
		response = requests.get(urlStr, headers=self._authHeaders)
		if self._isValid(response):
			activityListJson = response.json()
			activityList = activityListJson["activities-log-steps"]
			return activityList
		else:
			return []

	# Helper - deletes an activity and returns True if successful
	def _deleteActivity(self, logId):
		deleteActivityUrl = format("activities/%s.json" % (str(logId),))
		urlStr = self.fbBaseUrl + deleteActivityUrl
		response = requests.delete(urlStr, headers=self._authHeaders)
		if response.status_code == 204:
			return True
		else:
			logging.error(format(" Activity %d was not successfully deleted." % (logId,)))
			return False

	# Helper - gets the user's step goal. If the request is unsuccessful,
	# returns a default value of 1 million.
	def _getStepGoal(self):
		goalSummaryUrl =  format("activities/goals/%s.json" % (self._goalPeriod,))
		urlStr = self.fbBaseUrl + goalSummaryUrl
		response = requests.get(urlStr, headers=self._authHeaders)
		if self._isValid(response):
			return response.json()["goals"]["steps"]
		else:
			return 1000000

	# Helper - gets today's current step count. If the request is unsuccessful,
	# returns -1.
	def _getCurrentSteps(self): 
		date = self._getCurrentDate()
		dateActivityUrl = format("activities/date/%s.json" % (date,))
		urlStr = self.fbBaseUrl + dateActivityUrl
		response = requests.get(urlStr, headers=self._authHeaders)
		if self._isValid(response):
			return response.json()["summary"]["steps"]
		else:
			return -1
		
	# Helper - logs an activity containing the number of steps specified in 
	# newStepCount, and returns True if successful
	def _logStepActivity(self, newStepCount):
		activityUrl = "activities.json"
		urlStr = self.fbBaseUrl + activityUrl
		params = {
			"activityId" : '90013', # Walking (activityId=90013)
			"startTime" : self._getCurrentTime(), # HH:mm:ss
			"durationMillis" : 3600000, # 3,600,000 ms = 1 hr
			"date" : self._getCurrentDate(), # YYYY-MM-dd
			"distance" : newStepCount,
			"distanceUnit" : "steps"
		}
		response = requests.post(urlStr, headers=self._authHeaders, params=params)
		if self._isValid(response):
			loggedActivity = response.json()
			return True
		else:
			return False

	# Helper - returns current date as a string in YYYY-MM-dd format
	def _getCurrentDate(self):
		now = datetime.datetime.now()
		dateStr = format("%d-%02d-%02d" % (now.year, now.month, now.day))
		return dateStr

	# Helper - returns current time as a string in HH:mm:ss format
	def _getCurrentTime(self):
		now = datetime.datetime.now()
		timeStr = format("%02d:%02d:%02d" % (now.hour, now.minute, now.second))
		return timeStr

	# Helper - returns the past Sunday in YYYY-MM-dd format
	def _getSunday(self):
		today = datetime.date.today()
		todayWeekday = (today.weekday() + 1) % 7	# SUN = 0, MON = 1, ... , SAT = 6
		sun = today - datetime.timedelta(todayWeekday)
		sunStr = format("%d-%02d-%02d" % (sun.year, sun.month, sun.day))
		return sunStr

	# Helper - makes sure HTTP requests are successful
	def _isValid(self, response):
		if response.status_code >= 300:
			systemLogger.error(format(" Request could not be completed. Error: %d %s" 
					% (response.status_code, response.text)))
			return False
		else:
			return True
