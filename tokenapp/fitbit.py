#This class contains many of the API calls to Fitbit

import requests, sys, datetime, json

class Fitbit:
	dbPath = "data/db.json"
	db = TinyDB(self.dbPath)
	_fbTok = ''
	authHeaders = {}
	baseURL = 'https://api.fitbit.com/1/user/-/'

	def __init__(self, email):
		self._loadAccessInfo(email)
		self.authHeaders = {'Authorization': 'Bearer ' + self._fbTok}

	# Reads user's token from file
	def _loadAccessInfo_old(self):
		rawJsonStr = ""
		with open("data/fb.json", "r") as file:
			rawJsonStr = file.read()
		jsonObj = json.loads(rawJsonStr)
		self._fbTok = jsonObj["userToken"]

	# Gets user's access token from tinydb
	def _loadAccessInfo(self, email):
		user = Query()
		userInfo = db.search(user.email == email)[0]
		self._fbTok = userInfo["fbAccessToken"]

	# Given a percentage increase (from WeConnect), updates the progress towards the step goal
	def update(self, percent):
		prevSteps = self.getCurrentSteps()
		print("Previous step count:")
		print(prevSteps)
		numSteps = int(percent * self.getDailyActivityGoals())
		print("Added steps:")
		print(numSteps)
		self.logStepActivity(numSteps)
		print("New step count:")
		print(prevSteps + numSteps)

	# Used if WeConnect progress decreased
	def resetAndUpdate(self, percent):
		# Deletes all Fitbit step activities for the day
		dailyActivities = self.getDailyStepActivities()
		for activity in dailyActivities:
			logId = activity["logId"]
			print(logId)
			self.deleteActivity(logId)

		# Updates Fitbit with the new percentage
		self.update(percent)

	def getDailyStepActivities(self):
		activityListUrl = "activities/date/"+self._getCurrentDate()+".json"
		urlStr = self.baseURL + activityListUrl
		print(urlStr)
		response = requests.get(urlStr, headers=self.authHeaders)
		activityListJson = response.json()
		print(activityListJson)
		activityList = activityListJson["activities"]
		print(len(activityList))
		return activityList

	# DELETE - Activity
	# Returns True if Activity successfully deleted
	def deleteActivity(self, logId):
		deleteActivityUrl = "activities/" + str(logId) + ".json"
		urlStr = self.baseURL + deleteActivityUrl
		print(urlStr)
		response = requests.delete(urlStr, headers=self.authHeaders)
		if response.status_code == 204:
			return True
		else:
			return False

	#-GET- TRACKERS
	def getDevices(self):
		#summary of all goals
		devicesURL =  "devices.json"
		urlStr = self.baseURL + devicesURL
		devicesRaw = requests.get(urlStr, headers=self.authHeaders)
		devices = devicesRaw.json()
		print(devices)
		#for i in range(0, devices.length):
		#	print(devices[i]["deviceVersion"] + " is a " + devices[i]["type"])
		return devices

	#-GET- DAILY ACTIVITY GOALS
	def getDailyActivityGoals(self):
		#summary of all goals
		dailyGoalSummaryURL =  "activities/goals/daily.json"
		urlStr = self.baseURL + dailyGoalSummaryURL
		dailyGoals = requests.get(urlStr, headers=self.authHeaders)
		dailyGoalsJson = dailyGoals.json()
		#print dailyGoalsJson
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

	#-POST- CHANGE WEEKLY ACTIVITY STEP GOAL
	def changeWeeklyStepGoal(self, newStepGoal):
		goalURL = "activities/goals/weekly.json"
		urlStr = self.baseURL + goalURL
		params = {
			"period" : "weekly",
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
			"startTime" : self._getCurrentTime(), #HH:mm:ss
			"durationMillis" : 3600000, #60K ms = 1 min, 
			"date" : self._getCurrentDate(),
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

	def _getCurrentTime(self):
		now = datetime.datetime.now()
		timeStr = format("%02d:%02d:%02d" % (now.hour, now.minute, now.second))
		return timeStr
	
	#read the fitbit token you want to use from wherever it's stored
	def _readFromFile(self):
		global fbTok
		with open('sampleProfile.json') as json_data:
			data = json.load(json_data)
			fbTok = data["access_token"]

	def _isValid(self, result):
		if result.status_code >= 300:
			print("Request could not be completed:", str(result.status_code),
					result.text)
			return False
		else:
			return True
