#This file contains many of the API calls to fitbit
import requests, sys, datetime, json


fbTok = 'enteryourincrediblylongtokenhere' #or better, import it from a file, i.e. '<userID>.json'
authHeaders = {'Authorization': 'Bearer ' + fbTok }
baseURL = 'https://api.fitbit.com/1/user/-/'


#-GET- DAILY ACTIVITY GOALS
def getDailyActivityGoals():
	#summary of all goals
	dailyGoalSummaryURL =  "activities/goals/daily.json"
	urlStr = baseURL+dailyGoalSummaryURL
	dailyGoal = requests.get(urlStr, headers=authHeaders)
	print (dailyGoal.json())

#-GET- STEP COUNT BY DATE
def getCurrentSteps(): 
	#by date - default to current date
	date = _getCurrentDate()
	dateActivityURL = "activities/date/"+date+'.json'
	urlStr = baseURL+dateActivityURL
	dateActivity = requests.get(urlStr, headers=authHeaders)
	activities = dateActivity.json()	
	print (activities["summary"]["steps"])
	

	
#-POST- CHANGE DAILY ACTIVITY STEP GOAL
def changeDailyStepGoal():
	goalURL = "activities/goals/daily.json"
	urlStr = baseURL+activityURL
	params = {
	"period" : "daily",
	"type" : "steps",
	"value" : "30000"
	}
	changeGoal = requests.post(urlStr, headers=authHeaders, params=params)
	print (changeGoal.json())
	
		
#-POST- LOG A STEP ACTIVITY 
def logStepActivity():
	activityURL = "activities.json"
	urlStr = baseURL+activityURL
	params = {
	"activityId" : '90013', #Walking (activityId=90013), Running (activityId=90009)
	"activityName" : "wc_dummy",
	"startTime" : "08:10:03", #HH:mm:ss
	"durationMillis" : 360000, #60K ms = 1 min, 
	"date" : "2017-11-02",
	"distance" : 1000,
	"distanceUnit" : "steps"
	}
	loggedActivity = requests.post(urlStr, headers=authHeaders, params=params)
	print (loggedActivity)	

#helper - returns current date as a string in YYYY-MM-dd format
def _getCurrentDate():
	now = datetime.datetime.now()
	dateStr = format("%d-%02d-%02d" % (now.year, now.month, now.day))
	return dateStr	
	
#read the fitbit token you want to use from wherever its stored
def _readFromFile():
	global fbTok
	with open('sampleProfile.json') as json_data:
		data = json.load(json_data)
		fbTok = data["access_token"]

	
		