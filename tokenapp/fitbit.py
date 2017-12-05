#This class contains many of the API calls to Fitbit

import requests, sys, datetime, json

class Fitbit:
	_fbTok = ''
	authHeaders = {}
	baseURL = 'https://api.fitbit.com/1/user/-/'

	def __init__(self):
		self._loadAccessInfo()
		self.authHeaders = {'Authorization': 'Bearer ' + self._fbTok}

	# Reads user's token from file
	def _loadAccessInfo(self):
		rawJsonStr = ""
		with open("data/fb.json", "r") as file:
			rawJsonStr = file.read()
		jsonObj = json.loads(rawJsonStr)
		self._fbTok = jsonObj["userToken"]

	# Given a percentage (from WeConnect), updates the progress towards the step goal
	def update(self, percent):
		numSteps = int(percent * self.getDailyActivityGoals())
		print("The number of steps I will send to Fitbit is " + numSteps)
		self.logStepActivity(numSteps)

	#-GET- DAILY ACTIVITY GOALS
	def getDailyActivityGoals(self):
		#summary of all goals
		dailyGoalSummaryURL =  "activities/goals/daily.json"
		urlStr = self.baseURL + dailyGoalSummaryURL
		dailyGoals = requests.get(urlStr, headers=self.authHeaders)
		dailyGoalsJson = dailyGoals.json()
		print dailyGoalsJson
		return dailyGoalsJson["goals"]["steps"]

	#-GET- STEP COUNT BY DATE
	def getCurrentSteps(self): 
		#by date - default to current date
		date = self._getCurrentDate()
		dateActivityURL = "activities/date/"+date+'.json'
		urlStr = self.baseURL+dateActivityURL
		dateActivity = requests.get(urlStr, headers=self.authHeaders)
		activities = dateActivity.json()
		#print (activities["summary"]["steps"])
		return activities["summary"]["steps"]
	
	#-POST- CHANGE DAILY ACTIVITY STEP GOAL
	def changeDailyStepGoal(self, newStepGoal):
		goalURL = "activities/goals/daily.json"
		urlStr = self.baseURL+goalURL
		params = {
			"period" : "daily",
			"type" : "steps",
			"value" : newStepGoal
		}
		changeGoal = requests.post(urlStr, headers=self.authHeaders, params=params)
		#print (changeGoal.json())
		return changeGoal.json()
		
	#-POST- LOG A STEP ACTIVITY 
	def logStepActivity(self, newStepCount):
		activityURL = "activities.json"
		urlStr = self.baseURL + activityURL
		params = {
			"activityId" : '90013', #Walking (activityId=90013), Running (activityId=90009)
			"activityName" : "wc_dummy",
			"startTime" : "08:10:03", #HH:mm:ss
			"durationMillis" : 360000, #60K ms = 1 min, 
			"date" : "2017-11-02",
			"distance" : newStepCount,
			"distanceUnit" : "steps"
		}
		result = requests.post(urlStr, headers=self.authHeaders, params=params)
		if self._isValid(result):
			loggedActivity = result.json()
			print(loggedActivity)
			return True
		else:
			return False

	#helper - returns current date as a string in YYYY-MM-dd format
	def _getCurrentDate(self):
		now = datetime.datetime.now()
		dateStr = format("%d-%02d-%02d" % (now.year, now.month, now.day))
		return dateStr
	
	#read the fitbit token you want to use from wherever it's stored
	def _readFromFile(self):
		global fbTok
		with open('sampleProfile.json') as json_data:
			data = json.load(json_data)
			fbTok = data["access_token"]

	def _isValid(self, result):
		if result.status_code != 200:
			print("Request could not be completed:", str(result.status_code),
					result.text)
			return False
		else:
			return True