# weconnect.py
# This class contains the API calls to WEconnect (except for the login).
# Created by Abigail Franz
# Last modified by Abigail Franz on 1/29/2018

import datetime, json, logging, requests

class WeConnect:
	wcBaseUrl = "https://palalinq.herokuapp.com/api"
	_wcUserId = ""
	_wcAccessToken = ""
	_goalPeriod = ""
    
	def __init__(self, wcUserId, wcAccessToken, goalPeriod):
		self._wcUserId = wcUserId
		self._wcAccessToken = wcAccessToken
		self._goalPeriod = goalPeriod
		#logging.basicConfig(filename="logs/powertoken.log", level=logging.INFO)

	# Polls WEconnect for changes in progress
	# -1 denotes a failed request
	def poll(self):
		start, end = "", ""
		if self._goalPeriod == "daily":
			start, end = self._getToday()
		elif self._goalPeriod == "weekly":
			start, end = self._getWeek()
		return self._getProgress(start, end)

	# Helper - gets a list of progress for all activities within a specified
	# time range. Dates in format "YYYY-MM-dd"
	def _getProgress(self, fromDate, toDate):
		requestUrl = format("%s/People/%s/activities/progress?access_token=%s&from=%s&to=%s"
				% (self.wcBaseUrl, self._wcUserId, self._wcAccessToken, fromDate, toDate))
		response = requests.get(requestUrl)
		if self._isValid(response):
			progress = response.json()
			completed = progress["events"]["completed"]
			total = progress["events"]["total"]
			percent = float(completed) / float(total)
			#outputLogger.info(format(" Progress: %d / %d = %f" % (completed, total, percent)))
			return percent
		else:
			return -1

	# Helper - returns two formatted strings representing the date of the past
	# Sunday and the upcoming Saturday (for countries where Sunday is the first
	# day of the week)
	def _getWeek(self):
		today = datetime.date.today()
		todayWeekday = (today.weekday() + 1) % 7	# SUN = 0, MON = 1, ... , SAT = 6
		sun = today - datetime.timedelta(todayWeekday)
		sat = today + datetime.timedelta(6 - todayWeekday)
		sunStr = format("%d-%02d-%02d" % (sun.year, sun.month, sun.day))
		satStr = format("%d-%02d-%02d" % (sat.year, sat.month, sat.day))
		return sunStr, satStr

	# Helper - returns two formatted strings representing today at midnight and today
	# at 11:59 PM
	def _getToday(self):
		today = datetime.datetime.now()
		start = format("%d-%02d-%02dT%02d:%02d:%02d" % (today.year, today.month, today.day, 0, 0, 0))
		end = format("%d-%02d-%02dT%02d:%02d:%02d" % (today.year, today.month, today.day, 23, 59, 59))
		return start, end

	# Helper - makes sure HTTP requests are successful
	def _isValid(self, response):
		if response.status_code >= 300:
			systemLogger.error(format(" Request could not be completed. Error: %d %s" 
					% (response.status_code, response.text)))
			return False
		else:
			return True