"""
Contains various helpers for use by the Flask application.\n
Created by Abigail Franz on 3/13/2018\.n
Last modified by Abigail Franz on 5/5/2018.
"""
import logging, sys
import json, requests
from datetime import datetime, timedelta, MAXYEAR
#from background import db
#from app.models import Activity

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


WC_URL = "https://palalinq.herokuapp.com/api/People"
WC_DATE_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
TODAY = datetime(datetime.now().year, datetime.now().month, datetime.now().day)

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


def get_wc_activities(wc_id, wc_token):
	"""
	Pulls all of a user's activities from the WEconnect backend and parses
	information about them to prepare for stores. Returns a list of activity dicts

	:param a user's weconnect id, token
	"""
	url = "{}/{}/activities?access_token={}".format(WC_URL, wc_id, 
			wc_token)
	response = requests.get(url)
	if response.status_code != 200:
		# Return an empty list if the request was unsuccessful
		return []
	parsed = response.json()

	#TODO: EVERYTHING PAST HERE MODIFIED TO use WECONNECT.PY
	# Data to use: user, activity
	acts = []
	
	for p in parsed:
		act = wc_json_to_db(p)
		acts.append(act)
	'''
	for item in parsed:
		activity = wc_json_to_db(item, user)
		if activity.expiration > datetime.now():
			# Add the activity to the database if it's unexpired.
			db.session.add(activity)
			acts.append(activity)
	db.session.commit()
	'''
	return acts
	
#def wc_json_to_db(wc_act, user):
def wc_json_to_db(wc_act):
	"""
	Given a JSON activity object from WEconnect, convert it to an activity dict
	object compatible with the database.

	:param dict wc_act: an activity from WEconnect in JSON format
	return activity{ id, name, expiration, user=None}
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
	
	activity = {}
	activity["id"] = wc_act["activityId"]
	activity["name"] = wc_act["name"]
	activity["expiration"] = expiration
	activity["user"] = None
	#activity = Activity(wc_act_id=wc_act["activityId"], name=wc_act["name"],
	#		expiration=expiration, user=user)
	return activity

def complete_fb_login(fb_response):
	"""
	Extract the Fitbit access token from the response and return it, along with
	the PowerToken username embedded in the URL string that was sent back from
	Fitbit.

	:param dict fb_response: the data returned from Fitbit (in JSON format)
	"""
	data_utf = fb_response.decode("utf-8")
	data_json = json.loads(data_utf)
	logging.debug(data_json)
	return data_json["tok"], data_json["username"]
	
def fb_updateUserGoal(fbtoken):	

	BASE_URL = "https://api.fitbit.com/1/user/-"
	url = "{}/activities/goals/daily.json".format(BASE_URL)
	new_step_goal = 100000
	params = {
		"period" : "daily",
		"type" : "steps",
		"value" : new_step_goal
	}	
	auth_headers = {"Authorization": "Bearer " + fb_token}
	response = requests.post(url, headers=auth_headers, params=params)
	if response.status_code == 200:
		return response.json()["goals"]["steps"]