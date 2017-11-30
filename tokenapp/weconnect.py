import datetime, json, requests, sys, time

class WeConnect:
	wcBaseUrl = "https://palalinq.herokuapp.com/api"
	wcAccessFile = "data/wc.json"
	fbAccessFile = "data/fb.json"
	_userEmail = ""
	_userPwd = ""
	_wc_userId = ""
	_wc_userToken = ""
	_fb_userId = ""
	_fb_userToken = ""

	dailyStepGoal = 1000000
    
	def __init__(self):
		self._loadAccessInfo()

	def _loadAccessInfo(self):
		with open(self.wcAccessFile, "r") as file:
			rawJsonStr = file.read()
			jsonObj = json.loads(rawJsonStr)
			self._wc_userId = jsonObj["userId"]
			self._wc_userToken = jsonObj["userToken"]

	# Will probably spawn off a new thread to do the busy waiting
	def listenForWcChange(self):
		while True:
			# Waits 15 min (800 sec), then polls WEconnect
			time.sleep(800)
			self.poll()

	# Polls WEconnect for percent of daily activities completed
	def poll(self):
		temp = datetime.datetime(1977, 1, 1)
		d = temp.today()
		currentDate = str(d.year) + "-" + str(d.month) + "-" + str(d.day)
		currentTime = str(d.hour) + ":" + str(d.minute) + ":" + str(d.second)
		beginDate = currentDate + "T00:00:00"
		endDate = currentDate + "T" + currentTime
		percentProgress = self.getProgress(beginDate, endDate)
		if percentProgress == -1:
			print("Something went wrong in sending the request...")
			return False
		return percentProgress

	# GET a list of progress for all activities
	# Dates in format 'YYYY-MM-DD'
	def getProgress(self, fromDate, toDate):
		requestUrl = self.wcBaseUrl + "/People/" + self._wc_userId + \
				"/activities/progress?access_token=" + self._wc_userToken + \
				"&from=" + fromDate + "&to=" + toDate
		print(requestUrl)
		result = requests.get(requestUrl)
		if self._isValid(result):
			progress = result.json()
			print("Total vs Completed Events in ", fromDate, "to ", toDate, ": ",
					progress["events"]["completed"],"/", progress["events"]["total"])
			percent = int(progress["events"]["completed"]) / int(progress["events"]["total"])
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
