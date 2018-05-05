"""
Contains various helpers for use by the Flask application.\n
Created by Abigail Franz on 3/13/2018\.n
Last modified by Abigail Franz on 5/5/2018.
"""

import json, requests
from datetime import datetime, timedelta, MAXYEAR
from app import db
from app.models import Activity

WC_URL = "https://palalinq.herokuapp.com/api/People"
WC_DATE_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
TODAY = datetime(datetime.now().year, datetime.now().month, datetime.now().day)

def login_to_wc(email, password):
	"""
	Log user into WEconnect, produce an ID and access token that will last 90
	days. Return False if the login was unsuccessful; otherwise, return the ID
	and token in a tuple.

	:param String email: the user's WEconnect username (email address)
	:param String password: the user's WEconnect password
	"""
	url = "{}/login".format(WC_URL)
	data = {"email": email, "password": password}
	result = requests.post(url, data=data)
	if result.status_code != 200:
		return False
	jres = result.json()
	wc_id = str(jres["accessToken"]["userId"])
	wc_token = str(jres["accessToken"]["id"])
	return (wc_id, wc_token)

def get_wc_activities(user):
	"""
	Pulls all of a user's activities from the WEconnect backend and stores
	information about them in the database. Returns a list of app.model.Activity
	objects.

	:param app.models.User user: a user from the database
	"""
	url = "{}/{}/activities?access_token={}".format(WC_URL, user.wc_id, 
			user.wc_token)
	response = requests.get(url)
	if response.status_code != 200:
		# Return an empty list if the request was unsuccessful
		return []
	parsed = response.json()
	acts = []
	for item in parsed:
		activity = wc_json_to_db(item, user)
		if activity.expiration > datetime.now():
			# Add the activity to the database if it's unexpired.
			db.session.add(activity)
			db.session.commit()
			acts.append(activity)
	return acts
	
def wc_json_to_db(wc_act, user):
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
			expiration=expiration, user=user)
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
	return data_json["tok"], data_json["username"]