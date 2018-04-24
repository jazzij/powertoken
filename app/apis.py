"""
Contains the API calls for WEconnect and a helper that
processes the login response from the Fitbit API endpoint.\n
Created by Abigail Franz on 3/13/2018\.n
Last modified by Abigail Franz on 4/16/2018.
"""

import json, requests
from datetime import datetime, timedelta, MAXYEAR
from app import db
from app.models import Activity

def login_to_wc(email, password):
	"""
	Log user into WEconnect, produce an ID and access token that will last 90
	days. Return False if the login was unsuccessful; otherwise, return the ID
	and token.
	"""
	url = "https://palalinq.herokuapp.com/api/People/login"
	data = {"email": email, "password": password}
	result = requests.post(url, data=data)
	if result.status_code != 200:
		return False
	jres = result.json()
	wc_id = str(jres["accessToken"]["userId"])
	wc_token = str(jres["accessToken"]["id"])
	return (wc_id, wc_token)

def get_wc_activities(user):
	url = "https://palalinq.herokuapp.com/api/people/{}/activities?access_token={}".\
			format(user.wc_id, user.wc_token)
	response = requests.get(url)
	if response.status_code == 200:
		parsed = response.json()
		acts = []
		for item in parsed:
			activity = wc_json_to_db(item, user)
			if activity.expiration > datetime.now():
				db.session.add(activity)
				db.session.commit()
				acts.append(activity)
		return acts
	else:
		return []

def wc_json_to_db(wc_act, user):
	"""
	Given a JSON activity object from WEconnect, convert it to an Activity
	object compatible with the database.

	:param dict wc_act: an activity from WEconnect in JSON format
	"""
	# Determines the start and end times
	ts = datetime.strptime(wc_act["dateStart"], "%Y-%m-%dT%H:%M:%S.%fZ")
	te = ts + timedelta(minutes=wc_act["duration"])

	# Determines the expiration date (if any)
	expiration = datetime(MAXYEAR, 12, 31)
	if wc_act["repeat"] == "never":
		expiration = te
	if wc_act["repeatEnd"] != None:
		expiration = datetime.strptime(wc_act["repeatEnd"], "%Y-%m-%dT%H:%M:%S.%fZ")

	activity = Activity(activity_id=wc_act["activityId"], name=wc_act["name"],
			start_time=ts, end_time=te, expiration=expiration,
			repeat=wc_act["repeat"], user=user)
	return activity

def complete_fb_login(response_data):
	"""
	Extract the Fitbit access token from the response and return it.
	"""
	data_utf = response_data.decode("utf-8")
	data_json = json.loads(data_utf)
	return data_json["tok"], data_json["username"]