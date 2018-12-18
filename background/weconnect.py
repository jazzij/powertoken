"""
Contains the API calls to WEconnect.\n
Created by Abigail Franz.\n
Last modified by Abigail Franz on 4/30/2018.
"""

from datetime import datetime
import json, logging, requests
from db import session
from models import User, Activity, Event, Error

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


WC_URL = "https://palalinq.herokuapp.com/api/People"
WC_DATE_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
TODAY = datetime(datetime.now().year, datetime.now().month, datetime.now().day)


DATE_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
BASE_URL = "https://palalinq.herokuapp.com/api/people"

def check_wc_token_status(wc_user_id, wc_token):
	logging.info("CHECKING STATUS")
	"""
		CHECK TOKEN STATUS (401 AUTH ERROR)
	"""
	url = "{}/{}?access_token={}".format(WC_URL, wc_user_id, wc_token) 
	result = requests.get(url)
	logging.debug("Result: {}".format(result.status_code))
	if result.status_code != 200:
		print("Response: {}").format("Token invalid" if result.status_code == 401 else result.status_code)
		return False
	else:
		print("Token for User {} is good").format(wc_user_id)
		return True

def login_to_wc(email, password):
	"""
	Log user into WEconnect, produce an ID and access token that will last 90
	days. Return False if the login was unsuccessful; otherwise, return the ID
	and token in a tuple.
	
	Assumptions: People already have a WeConnect account (email)
	Outcome: all successful login requests return a id, and NEW access token

	:param String email: the user's WEconnect username (email address)
	:param String password: the user's WEconnect password
	"""
	url = "{}/login".format(WC_URL)
	data = {"email": email, "password": password}
	result = requests.post(url, data=data)
	if result.status_code != 200:
		return False, ()
		
	jres = result.json()
	wc_id = str(jres["accessToken"]["userId"])
	wc_token = str(jres["accessToken"]["id"])
	logging.debug("WC Login attempt returns: {}".format(wc_id))
	if wc_id is None:
		return False, ()
	else:
		return True, (wc_id, wc_token)


def get_activities(user):
	"""
	OUTDATED?
	Fetch all the user's WEconnect activities. Return an empty list if the
	request is unsuccessful.

	:param background.models.User user
	"""
	logging.debug("YOU'VE ACCESSED WC.get_activities(). This is deprecated")
	pass
	
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

def set_wc_activities(wc_user_id, wc_user_token):
	"""
	Pulls all of a user's activities from the WEconnect backend and stores
	information about them in the database. Returns a list of app.model.Activity
	objects.

	:param app.models.User user: a user from the database
	"""
	url = "{}/{}/activities?access_token={}".format(WC_URL, wc_user_id, wc_user_token)
	response = requests.get(url)
	if response.status_code != 200:
		# Return an empty list if the request was unsuccessful
		return []
	wc_acts = response.json()
	for act in wc_acts:
		activity = createNewActivity(act, wc_user_id)
		if activity.expiration > datetime.now():
			# Add the activity to the database if it's unexpired.
			session.add(activity)
	try:
		db.session.commit()
		print("Added {} activities for {}").format(len(wc_acts), wc_user_id)
	except:
		print("Could not add activities for {}").format(wc_user_id)
		db.rollback()


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


def createNewEvent(js_event):
	#eid, start_time, didCheckin, day_id=None, activity_id
	
	startTime = datetime.strptime(ev["dateStart"], WC_DATE_FMT)
	newEvent = Event(eid=event["eid"], start_time=startTime, activity_id=ev["activityId"], completed=ev["didCheckin"])

	return newEvent



def createNewActivity(wc_act, wc_user_id):
	"""
	Given a JSON activity object from WEconnect, convert it to an Activity
	object compatible with the database.

	:param dict wc_act: an activity from WEconnect in JSON format
	:param app.models.User user
	"""
	# Determine the start and end times
	ts = datetime.strptime(wc_act["dateStart"], WC_DATE_FMT)
	te = ts + timedelta(minutes=wc_act["duration"])

	# Determine the expiration date (if any)
	expiration = datetime(MAXYEAR, 12, 31)
	if wc_act["repeat"] == "never":
		expiration = te
	if wc_act["repeatEnd"] != None:
		expiration = datetime.strptime(wc_act["repeatEnd"], WC_DATE_FMT)

	activity = Activity(wc_act_id=wc_act["activityId"], name=wc_act["name"],
			expiration=expiration, wc_user_id=wc_user_id)
	return activity