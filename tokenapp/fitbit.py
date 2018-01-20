# fitbit.py
# This class contains the API calls to Fitbit (excpt for the login).
# Created by: Abigail Franz
# Last modified by: Abigail Franz on 1/20/2018

import requests, sys, datetime, json

class Fitbit:
	baseURL = 'https://api.fitbit.com/1/user/-/'
	_authHeaders = {}

	def __init__(self, fbAccessToken):
		self._authHeaders = {'Authorization': 'Bearer ' + fbAccessToken}

	# Changes the daily step goal to newStepGoal and returns True if successful
	def changeDailyStepGoal(self, newStepGoal):
		goalURL = "activities/goals/daily.json"
		urlStr = self.baseURL + goalURL
		params = {
			"period" : "daily",
			"type" : "steps",
			"value" : newStepGoal
		}
		response = requests.post(urlStr, headers=self._authHeaders, params=params)
		if self._isValid(response):
			newGoal = response.json()["goals"]["steps"]
			print("New daily step goal: %d" % (newGoal,))
			return True
		else:
			print("Error changing daily step goal: %d" % (response.status_code,))
			return False

	# Given a percentage increase (from WEconnect), updates the progress
	# towards the step goal
	def update(self, percent):
		prevSteps = self._getCurrentSteps()
		print("Previous step count: %d" % (prevSteps,))
		numSteps = int(percent * self._getDailyActivityGoals())
		self._logStepActivity(numSteps)
		print("Added steps: %d" % (numSteps,))
		print("New step count: %d" % (prevSteps + numSteps,))

	# Used if WeConnect progress decreased
	def resetAndUpdate(self, percent):
		# Deletes all Fitbit step activities for the day
		dailyActivities = self._getDailyStepGoal()
		for activity in dailyActivities:
			logId = activity["logId"]
			self._deleteActivity(logId)

		# Updates Fitbit with the new percentage
		self.update(percent)

	# Helper - returns a list of all the activities the user has completed today
	def _getDailyStepActivities(self):
		activityListUrl = "activities/date/" + self._getCurrentDate() + ".json"
		urlStr = self.baseURL + activityListUrl
		response = requests.get(urlStr, headers=self._authHeaders)
		activityListJson = response.json()
		activityList = activityListJson["activities"]
		return activityList

	# Deletes an activity and returns True if successful
	def _deleteActivity(self, logId):
		deleteActivityUrl = "activities/" + str(logId) + ".json"
		urlStr = self.baseURL + deleteActivityUrl
		response = requests.delete(urlStr, headers=self._authHeaders)
		if response.status_code == 204:
			return True
		else:
			print("Activity %d was not successfully deleted." % (logId,))
			return False

	# Gets the user's daily step goal
	def _getDailyStepGoal(self):
		dailyGoalSummaryURL =  "activities/goals/daily.json"
		urlStr = self.baseURL + dailyGoalSummaryURL
		response = requests.get(urlStr, headers=self._authHeaders)
		if self._isValid(response):
			return response.json()["goals"]["steps"]
		else:
			return response.status_code

	# Gets today's current step count
	def _getCurrentSteps(self): 
		date = self._getCurrentDate()
		dateActivityURL = "activities/date/" + date + '.json'
		urlStr = self.baseURL + dateActivityURL
		response = requests.get(urlStr, headers=self._authHeaders)
		if self._isValid(response):
			return response.json()["summary"]["steps"]
		else:
			print("Couldn't get today's step count. Error %d: %s" % (response.status_code, response.text))
			return -1

	# Changes the weekly step goal to newStepGoal and returns True if successful
	def _changeWeeklyStepGoal(self, newStepGoal):
		goalURL = "activities/goals/weekly.json"
		urlStr = self.baseURL + goalURL
		params = {
			"period" : "weekly",
			"type" : "steps",
			"value" : newStepGoal
		}
		result = requests.post(urlStr, headers=self._authHeaders, params=params)
		if self._isValid(result):
			print(result.json())
			return True
		else:
			return False
		
	# Logs an activity containing the number of steps specified in newStepCount
	# Returns True if successful
	def _logStepActivity(self, newStepCount):
		activityURL = "activities.json"
		urlStr = self.baseURL + activityURL
		params = {
			"activityId" : '90013', # Walking (activityId=90013), Running (activityId=90009)
			"startTime" : self._getCurrentTime(), # HH:mm:ss
			"durationMillis" : 3600000, # 60K ms = 1 min, 
			"date" : self._getCurrentDate(),
			"distance" : newStepCount,
			"distanceUnit" : "steps"
		}
		response = requests.post(urlStr, headers=self._authHeaders, params=params)
		if self._isValid(response):
			loggedActivity = response.json()
			print(loggedActivity)
			return True
		else:
			print("Couldn't log step activity. Error %d: %s" % (response.status_code, response.text))
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

	# Helper - makes sure HTTP requests are successful
	def _isValid(self, result):
		if result.status_code >= 300:
			return False
		else:
			return True
