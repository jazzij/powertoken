"""
Contains the API calls for WEconnect and a helper that
processes the login response from the Fitbit API endpoint.\n
Created by Abigail Franz on 3/13/2018\.n
Last modified by Abigail Franz on 3/13/2018.
"""

import json, requests

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

def get_wc_activities(wc_id, wc_token):
	url = "https://palalinq.herokuapp.com/api/people/{}/activities?access_token={}".\
			format(wc_id, wc_token)
	response = requests.get(url)
	if response.status_code == 200:
		parsed = response.json()
		acts = []
		for item in parsed:
			expiration = extract_expiration(item)
			if expiration > datetime.now():
				acts.append({"id": item["activityId"], "name": item["name"]})
		return acts
	else:
		return []

def extract_expiration(activity):
	"""
	Given a JSON activity object from WEconnect, extract expiration.

	:param dict activity: an activity from WEconnect in JSON format
	"""
	# Determines the start and end times
	ts = datetime.strptime(activity["dateStart"], "%Y-%m-%dT%H:%M:%S.%fZ")
	te = ts + timedelta(minutes=activity["duration"])

	# Determines the expiration date (if any)
	expiration = datetime(MAXYEAR, 12, 31)
	if activity["repeat"] == "never":
		expiration = te
	if activity["repeatEnd"] != None:
		expiration = datetime.strptime(activity["repeatEnd"], "%Y-%m-%dT%H:%M:%S.%fZ")

	return expiration

def complete_fb_login(response_data):
	"""
	Extract the Fitbit access token from the response and return it.
	"""
	data_utf = response_data.decode("utf-8")
	data_json = json.loads(data_utf)
	return data_json["tok"], data_json["username"]