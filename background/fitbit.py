"""
Contains the API calls to Fitbit.\n
Created by Abigail Franz.\n
Last modified by Abigail Franz on 4/30/2018.
"""

from datetime import datetime
import json, logging, requests
from db import session
from models import Error

BASE_URL = "https://api.fitbit.com/1/user/-"
DATE_FMT = "%Y-%m-%d"

def change_step_goal(user, new_step_goal):
	"""
	Change the step goal to new_step_goal. Return the new step goal (or 0 if
	the request was unsuccessful).

	:param background.models.User user\n
	:param int new_step_goal
	"""
	url = "{}/activities/goals/daily.json".format(BASE_URL)
	params = {
		"period" : "daily",
		"type" : "steps",
		"value" : new_step_goal
	}
	auth_headers = {"Authorization": "Bearer " + user.fb_token}
	response = requests.post(url, headers=auth_headers, params=params)
	if response.status_code == 200:
		return response.json()["goals"]["steps"]
	else:
		error = Error(
			summary = "Couldn't change the step goal.",
			origin = "background/fitbit.py, in change_step_goal",
			message = response.json()["errors"][0]["message"],
			user = user
		)
		session.add(error)
		session.commit()
		return 0

def update_progress(user, progress):
	"""
	Reset Fitbit to receive new step activities and return the number of
	steps added; if there's an error, return an Error.

	:param background.models.User user\n
	:param float progress: WEconnect progress as a decimal
	"""
	# Delete existing Fitbit step activities for the day
	step_activities = get_daily_step_activities(user)
	for activity in step_activities:
		delete_activity(user, activity["logId"])

	# Update Fitbit with the new percentage
	new_steps = int(progress * get_step_goal(user))
	return log_step_activity(user, new_steps)

def get_daily_step_activities(user):
	"""
	Return a list of all the activities the user has completed today. If
	the request is unsuccessful, return an empty list.

	:param background.models.User user
	"""
	today = datetime.now().strftime(DATE_FMT)
	url = "{}/activities/date/{}.json".format(BASE_URL, today)
	auth_headers = {"Authorization": "Bearer " + user.fb_token}
	response = requests.get(url, headers=auth_headers)
	if response.status_code == 200:
		return response.json()["activities"]
	else:
		error = Error(
			summary = "Couldn't get today's step activities.",
			origin = "background/fitbit.py, in _get_daily_step_activities",
			message = response.json()["errors"][0]["message"],
			user = user
		)
		session.add(error)
		session.commit()
		return []

def delete_activity(user, log_id):
	"""
	Delete a step activity from the user's Fitbit endpoint. Return a Boolean
	indicating success.

	:param background.models.User user\n
	:param int log_id: identifier for Fitbit step activity
	"""
	url = "{}/activities/{}.json".format(BASE_URL, log_id)
	auth_headers = {"Authorization": "Bearer " + user.fb_token}
	response = requests.delete(url, headers=auth_headers)
	if response.status_code == 204:
		return True
	else:
		error = Error(
			summary = "Activity {} was not successfully deleted".format(log_id),
			origin = "background/fitbit.py, in delete_activity",
			message = response.json()["errors"][0]["message"],
			user = user
		)
		session.add(error)
		session.commit()
		return False

def get_step_goal(user):
	"""
	Get the user's step goal. If the request is unsuccessful, return a
	default value of 1 million.

	:param background.models.User user
	"""
	url = "{}/activities/goals/daily.json".format(BASE_URL)
	auth_headers = {"Authorization": "Bearer " + user.fb_token}
	response = requests.get(url, headers=auth_headers)
	if response.status_code == 200:
		return response.json()["goals"]["steps"]
	else:
		error = Error(
			summary = "Couldn't get step goal. Using 1,000,000 instead.",
			origin = "background/fitbit.py, in get_step_goal",
			message = response.json()["errors"][0]["message"],
			user = user
		)
		session.add(error)
		session.commit()
		return 1000000
		
def log_step_activity(user, new_step_count):
	"""
	Log a walking activity containing the number of steps specified in
	new_step_count. Return the new step count (0 if the POST request is
	unsuccessful).

	:param background.models.User user\n
	:param int new_step_count
	"""
	url = "{}/activities.json".format(BASE_URL)
	now = datetime.now()
	params = {
		"activityId": '90013',
		"startTime": now.strftime("%H:%M:%S"),
		"durationMillis": 3600000,
		"date": now.strftime("%Y-%m-%d"),
		"distance": new_step_count,
		"distanceUnit": "steps"
	}
	auth_headers = {"Authorization": "Bearer " + user.fb_token}
	response = requests.post(url, headers=auth_headers, params=params)
	if response == 200:
		return new_step_count
	else:
		error = Error(
			summary = "Couldn't log step activity.",
			origin = "background/fitbit.py, in _log_step_activity",
			message = response.json()["errors"][0]["message"],
			user = user
		)
		session.add(error)
		session.commit()
		return 0