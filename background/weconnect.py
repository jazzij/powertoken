"""
This class contains the API calls to WEconnect (except for the login).\n
Created by Abigail Franz\n
Last modified by Abigail Franz on 3/16/2018
"""

import datetime, json, logging, requests
from common import is_valid, logfile

"""Format for datetimes received from WEconnect"""
WC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

"""Base URL for WEconnect API calls"""
BASE_URL = "https://palalinq.herokuapp.com/api"

class WeConnect:
	"""
	Class encapsulating the WEconnect API calls.
	"""
	_wc_id = ""
	_wc_token = ""
	_goal_period = ""
    
	def __init__(self, wc_id, wc_token, goal_period):
		self._wc_id = wc_id
		self._wc_token = wc_token
		self._goal_period = goal_period
		logging.basicConfig(filename=logfile, level=logging.DEBUG, 
				format="%(asctime)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")

	def poll(self):
		"""
		Poll WEconnect for changes in progress. -1 denotes a failed request.
		"""
		start, end = self._get_today()
		daily_progress = self._get_progress(start, end)
		start, end = self._get_week()
		weekly_progress = self._get_progress(start, end)
		return daily_progress, weekly_progress

	def _get_progress(self, from_date, to_date):
		"""
		Get a list of progress for all activities within a specified time
		range. Dates in format YYYY-MM-dd.
		"""
		url = "{}/People/{}/activities/progress?access_token={}&from={}&to={}".\
				format(BASE_URL, self._wc_id, self._wc_token, from_date, to_date)
		response = requests.get(url)
		if is_valid(response):
			progress = response.json()
			completed = float(progress["events"]["completed"])
			total = float(progress["events"]["total"])

			# Handles the case where total = 0, to avoid division by 0
			if total == 0:
				return 0

			percent = completed / total
			return percent
		else:
			logging.error("Couldn't get WEconnect progress.")
			return -1

	def _get_week(self):
		"""
		Return two formatted strings representing the date of the past Sunday
		and the upcoming Saturday (for countries where Sunday is the first day
		of the week).
		"""
		today = datetime.date.today()
		today_weekday = (today.weekday() + 1) % 7
		sun = today - datetime.timedelta(today_weekday)
		sat = today + datetime.timedelta(6 - today_weekday)
		sun_str = format("%d-%02d-%02d" % (sun.year, sun.month, sun.day))
		sat_str = format("%d-%02d-%02d" % (sat.year, sat.month, sat.day))
		return sun_str, sat_str

	def _get_today(self):
		"""
		Return two formatted strings representing today at midnight and today
		at 11:59 PM.
		"""
		today = datetime.datetime.now()
		start = format("%d-%02d-%02dT%02d:%02d:%02d" 
				% (today.year, today.month, today.day, 0, 0, 0))
		end = format("%d-%02d-%02dT%02d:%02d:%02d" 
				% (today.year, today.month, today.day, 23, 59, 59))
		return start, end

def get_activities(wc_id, wc_token):
	"""
	Static function to fetch all activities for a user with given ID and token.
	"""
	url = "{}/people/{}/activities?access_token={}".format(BASE_URL, wc_id, wc_token)
	response = requests.get(url)
	if is_valid(response):
		return response.json()
	else:
		return None
