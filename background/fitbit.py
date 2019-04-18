"""
Contains the API calls to Fitbit.\n
Created by Abigail Franz, Sunny Parawala, Jasmine Jones \n
Last modified by Jasmine Jones, 4/2019.
"""
from math import ceil
from datetime import datetime, timedelta
import json, logging, requests
from database import db_session
from data.models import User, Error

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

BASE_URL = "https://api.fitbit.com/1/user/-"
DATE_FMT = "%Y-%m-%d"

DEFAULT_GOAL = 100000
STEPS_PER_POINT = .10 * DEFAULT_GOAL

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
		error_msg = response.text
		error = Error(
			summary = "Couldn't change the step goal.",
			origin = "background/fitbit.py, in change_step_goal",
			message = error_msg,
			user = user
		)
		db_session.add(error)
		db_session.commit()
		return -1

def get_step_goal(user):
	"""
	Get the user's step goal. 
	If the request is unsuccessful, return -1

	:param background.models.User user
	"""
	url = "{}/activities/goals/daily.json".format(BASE_URL)
	auth_headers = {"Authorization": "Bearer " + user.fb_token}
	response = requests.get(url, headers=auth_headers)
	if response.status_code == 200:
		return response.json()["goals"]["steps"]
	else:
		error_msg = response.json()
		error_msg = error_msg["errors"][0]
		error = Error(
			summary = "Couldn't get step goal.",
			origin = "background/fitbit.py, in get_step_goal",
			message = error_msg["message"],
			user = user
		)
		db_session.add(error)
		db_session.commit()
		return 0
	

def update_progress_decimal(user, progress):
	"""
	Reset Fitbit to receive new step activities and return the number of
	steps added; if there's an error, return an Error.

	:param background.models.User user\n
	:param float progress: WEconnect progress as a decimal
	"""
	#GET CURRENT STEPS
	#step_activities = get_daily_step_activities(user)
	#cur_steps = step_activities[0]["steps"]
	#logging.debug("found {} previous activities".format(num_activities))
	clear_user_log(user)
	
	# Update Fitbit with the new count, based on percentage
	goal = get_step_goal(user) or DEFAULT_GOAL
	new_steps = int(ceil(progress * goal))
	logging.debug("Logging new goal {} * {} = {} new steps".format(goal, progress, new_steps))
	
	log = log_step_activity(user, new_steps)
	return log

def update_progress_count(user, steps_to_add):

	old_steps = clear_user_log(user)
	
	#Update fitbit with new count
	stepCount = old_steps + steps_to_add
	log = log_step_activity(user, stepCount)
	logging.debug("Logging additional {} to get total {}".format(steps_to_add, log))

	return log

def clear_user_log(user):
	'''
		Deletes existing manual activity logs in user profile
		Returns number of steps represented in log
	'''
	step_activities = get_daily_step_activities(user)
	old_steps = 0
	for activity in step_activities:
		old_steps += activity["steps"]
		delete_activity(user, activity["logId"])
	return old_steps

def log_addl_steps(user, add_steps):
	#DEPRECATED
	# Count existing steps
	# Add new steps
	# Log old + new steps as updated count
	step_activities = get_daily_step_activities(user)
	cur_steps = step_activities[0]["steps"]
	
	updated_count = cur_steps + add_steps
	log = log_step_activity(user, updated_count)
	logging.debug("Logging additional {} to get total {}".format(add_steps, log))
	return log


	

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
		error_msg = response.text
		error = Error(
			summary = "Couldn't get today's step activities.",
			origin = "background/fitbit.py, in get_daily_step_activities",
			message = error_msg,
			user = user
		)
		db_session.add(error)
		db_session.commit()
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
		logging.debug("Deleted activity {}".format(log_id))
		return True
	else:
		error_msg = response.json()	
		error_msg = error_msg["errors"][0]
		error = Error(
			summary = "Activity {} was not successfully deleted".format(log_id),
			origin = "background/fitbit.py, in delete_activity",
			message = error_msg['message'],
			user = user
		)
		
		db_session.add(error)
		db_session.commit()
		return False


def log_step_activity(user, new_step_count, time=None):
	""" POST
	Log a walking activity containing the number of steps specified in
	new_step_count. Return the new step count (0 if the POST request is
	unsuccessful).

	:param background.models.User user\n
	:param int new_step_count
	"""	
	#POST new steps
	url = "{}/activities.json".format(BASE_URL)
	
	start_time = datetime.now()
	params = {
		"activityId": '90013',
		"startTime": start_time.strftime("%H:%M"),
		"durationMillis": 3600000, 
		"date": start_time.strftime("%Y-%m-%d"),
		"distance": new_step_count,
		"distanceUnit": "steps"
	}
	auth_headers = {"Authorization": "Bearer " + user.fb_token}
	response = requests.post(url, headers=auth_headers, params=params)
	if response.status_code == 201: #POST success is 201
		return new_step_count
	else:
		error_msg = response.text
		error = Error(
			summary = "Couldn't log step activity.",
			origin = "background/fitbit.py, in log_step_activity",
			message = error_msg,
			user = user
		)
		db_session.add(error)
		db_session.commit()
		return 0

def get_logged_activities(user, afterDate=None):
	#GET https://api.fitbit.com/1/user/-/activities/list.json
	#As written this duplicates functionality of get_daily_step_activity, returning a list of activities for a certain date
	url = "{}/activities/list.json".format(BASE_URL)
	
	if afterDate is None:
		now = datetime.now()
		yesterday = now - timedelta(days=1)
		afterDate = yesterday	

	params = {
		"afterDate": afterDate.strftime(DATE_FMT),
		"sort": 'asc',
		"limit": 20,
		"offset": 0,
	}	
	
	auth_headers = {"Authorization": "Bearer " + user.fb_token}
	response = requests.get(url, headers=auth_headers, params=params)

	if response.status_code == 200:
		return response.json()["activities"]	
	else:
		error_msg = response.text
		error = Error(
			summary = "Couldn't get activity log.",
			origin = "background/fitbit.py, in get_logged_activities",
			message = error_msg,
			user = user
		)
		db_session.add(error)
		db_session.commit()
		return []		
		

def get_dashboard_state(user, date=None):
	#GET /activities/steps/date/2017-12-05/1d.json	
	if date is None:
		date = datetime.now()
		
	url = "{}/activities/steps/date/{}/1d.json".format(BASE_URL, date.strftime(DATE_FMT))
	
	auth_headers = {"Authorization": "Bearer " + user.fb_token}
	response = requests.get(url, headers=auth_headers)

	if response.status_code == 200:
		return response.json()['activities-steps'][0]["value"]
	else:
		print("Error: {}".format(response.json()))
		return -1	

if __name__ == "__main__":
	from database import db_session, close_connection
	user = db_session.query(User).filter_by(username="jazzij").first()
	print( get_step_goal(user))
	
	before = datetime.now() - timedelta(hours = 1)
	print( log_step_activity(user, 500, time=before))
	print( log_step_activity(user, 200))
	#print( change_step_goal(user, 5000))
	#update_progress_decimal()
	#update_progress_count()
	print( get_logged_activities(user))
	print(get_dashboard_state(user))
	#print( get_daily_step_activities(user))
	#print("A:{}, entered:{}, from:{} on {} steps:{}".format(l["activityName"], l["logType"], l["source"]["id"], l["originalStartTime"], l["steps"]))

	close_connection()
