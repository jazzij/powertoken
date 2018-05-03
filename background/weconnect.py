"""
Contains the API calls to WEconnect.\n
Created by Abigail Franz.\n
Last modified by Abigail Franz on 4/30/2018.
"""

from datetime import datetime
import json, logging, requests
from db import session
from models import Error

DATE_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
BASE_URL = "https://palalinq.herokuapp.com/api/people"

def get_activities(user):
	"""
	Fetch all the user's WEconnect activities. Return an empty list if the
	request is unsuccessful.

	:param background.models.User user
	"""
	url = "{}/{}/activities?access_token={}".format(BASE_URL, user.wc_id,
			user.wc_token)
	response = requests.get(url)
	if response.status_code == 200:
		return response.json()
	else:
		error = Error(
			summary = "Couldn't get list of activities.",
			origin = "background/weconnect.py, in _get_activities",
			message = response.json()["error"]["message"],
			user = user
		)
		session.add(error)
		session.commit()
		return []

def get_todays_events(user):
	"""
	Get the activities-with-events that are happening today. Return an empty
	list if the request is unsuccessful.

	:param background.models.User user
	"""
	today = datetime.now()
	st = today.strftime("%Y-%m-%dT00:00:00")
	et = today.strftime("%Y-%m-%dT23:59:59")
	url = "{}/{}/activities-with-events?from={}&to={}&access_token={}".format(
			BASE_URL, user.wc_id, st, et, user.wc_token)
	response = requests.get(url)
	if response.status_code == 200:
		return response.json()
	else:
		error = Error(
			summary = "Couldn't get activities with events for {}".format(today),
			origin = "background/weconnect.py, in get_todays_events",
			message = response.json()["error"]["message"],
			user = user
		)
		session.add(error)
		session.commit()
		return []
