import datetime, json, requests, sys, time
from tinydb import TinyDB, Query

class WeConnect:
	wcBaseUrl = "https://palalinq.herokuapp.com/api"
	wcAccessFile = "data/wc.json"
	fbAccessFile = "data/fb.json"
	dbPath = "data/db.json"
	db = TinyDB(dbPath)
	_wc_userId = ""
	_wc_userToken = ""
	_fb_userId = ""
	_fb_userToken = ""

	dailyStepGoal = 1000000
    
	def __init__(self, email):
		self._loadAccessInfo(email)

	def _loadAccessInfo_old(self):
		with open(self.wcAccessFile, "r") as file:
			rawJsonStr = file.read()
			jsonObj = json.loads(rawJsonStr)
			self._wc_userId = jsonObj["userId"]
			self._wc_userToken = jsonObj["userToken"]

	# TODO: new function that uses tinydb
	def _loadAccessInfo(self, email):
		user = Query()
		userInfo = self.db.search(user.email == email)[0]
		self._wc_userId = userInfo["wcUserId"]
		self._wc_userToken = userInfo["wcAccessToken"]

	# Will probably spawn off a new thread to do the busy waiting
	def listenForWcChange(self):
		while True:
			# Waits 15 min (800 sec), then polls WEconnect
			time.sleep(800)
			self.poll()

	# Polls WEconnect for percent of daily activities completed
	def poll_old(self):
		beginDate = self._getCurrentDate() + "T00:00:00"
		endDate = self._getCurrentDate() + "T" + self._getCurrentTime()
		percentProgress = self.getProgress(beginDate, endDate)
		if percentProgress == -1:
			print("Something went wrong in sending the request...")
			return False
		return percentProgress

	def poll(self):
		#sun, sat = self._getWeek()
		start, end = self._getToday()
		percentProgress = self.getProgress(start, end)
		if percentProgress == -1:
			print("Something went terribly wrong in sending the request.")
			return -1
		return percentProgress

	# GET a list of progress for all activities
	# Dates in format 'YYYY-MM-dd'
	def getProgress(self, fromDate, toDate):
		requestUrl = self.wcBaseUrl + "/People/" + self._wc_userId + \
				"/activities/progress?access_token=" + self._wc_userToken + \
				"&from=" + fromDate + "&to=" + toDate
		print(requestUrl)
		response = requests.get(requestUrl)
		if self._isValid(response):
			progress = response.json()
			print("Total vs Completed Events from %s to %s: %d / %d" % (fromDate, toDate,
					progress["events"]["completed"], progress["events"]["total"],))
			percent = int(progress["events"]["completed"]) / int(progress["events"]["total"])
			print("As a percentage, thats %4.2f %" % (percent * 100,))
			return percent
		else:
			return -1

	def _isValid(self, result):
		if result.status_code != 200:
			print("Request could not be completed:", str(result.status_code),
					result.text)
			return False
		else:
			return True

	# Returns two formatted strings representing the date of the past Sunday and the
	# upcoming Saturday (for countries where Sunday is the first day of the week)
	def _getWeek(self):
		today = datetime.date.today()
		todayWeekday = (today.weekday() + 1) % 7	# SUN = 0, MON = 1, ... , SAT = 6
		sun = today - datetime.timedelta(todayWeekday)
		sat = today + datetime.timedelta(6 - todayWeekday)
		sunStr = format("%d-%02d-%02d" % (sun.year, sun.month, sun.day))
		satStr = format("%d-%02d-%02d" % (sat.year, sat.month, sat.day))
		return sunStr, satStr

	#helper - returns current date as a string in YYYY-MM-dd format
	def _getCurrentDate(self):
		now = datetime.datetime.now()
		dateStr = format("%d-%02d-%02d" % (now.year, now.month, now.day))
		return dateStr

	def _getToday(self):
		today = datetime.datetime.now()
		start = format("%d-%02d-%02dT%02d:%02d:%02d" % (today.year, today.month, today.day, 0, 0, 0))
		end = format("%d-%02d-%02dT%02d:%02d:%02d" % (today.year, today.month, today.day, 23, 59, 59))
		return start, end

	def _getCurrentTime(self):
		now = datetime.datetime.now()
		timeStr = format("%02d:%02d:%02d" % (now.hour, now.minute, now.second))
		return timeStr

