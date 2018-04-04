"""
Contains the API call for the WEconnect login and a related helper that
processes the response from the Fitbit API endpoint.\n
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

def complete_fb_login(response_data):
	"""
	Extract the Fitbit access token from the response and return it.
	"""
	data_utf = response_data.decode("utf-8")
	data_json = json.loads(data_utf)
	return data_json["tok"], data_json["username"]