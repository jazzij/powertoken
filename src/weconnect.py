# weconnect.py
# This class contains the API calls to WEconnect.
# Created by: Abigail Franz
# Last modified by: Abigail Franz on 1/20/2018

import datetime, json, requests, sys, time

class WeConnect:
	wcBaseUrl = "https://palalinq.herokuapp.com/api"
	_wcUserId = ""
	_wcAccessToken = ""
	dailyStepGoal = 1000000
    
	def __init__(self, wcUserId, wcAccessToken):
		self._wcUserId = wcUserId
		self._wcAccessToken = wcAccessToken

	# Polls WEconnect for changes in progress
	def poll(self):
		#sun, sat = self._getWeek()
		start, end = self._getToday()
		percentProgress = self._getProgress(start, end)
		if percentProgress == -1:
			print("Something went terribly wrong in sending the request.")
			return -1
		return percentProgress

	# Helper - gets a list of progress for all activities within a specified
	# time range. Dates in format "YYYY-MM-dd"
	def _getProgress(self, fromDate, toDate):
		requestUrl = self.wcBaseUrl + "/People/" + self._wcUserId + \
				"/activities/progress?access_token=" + self._wcAccessToken + \
				"&from=" + fromDate + "&to=" + toDate
		response = requests.get(requestUrl)
		if self._isValid(response):
			progress = response.json()
			print("Total vs Completed Events today: %d / %d" % 
				(progress["events"]["completed"], progress["events"]["total"],))
			percent = float(progress["events"]["completed"]) / float(progress["events"]["total"])
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
			print("Request could not be completed. Error: %d %s" % (response.status_code, response.text,))
			return False
		else:
			return True