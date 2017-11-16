# powertoken_setup.py
# Contains the WEconnect login function

import json
import os
import requests

wcLoginUrl = "https://palalinq.herokuapp.com/api/People/login"
filepath = "data/wc.json"

# Logs user into WEconnect and produces an access token that will last 90 days
def loginToWc(email, password):
	result = requests.post(wcLoginUrl, data={"email":email, "password":password})
	if result.status_code != 200:
		print("Login error")
		exit()
	jres = result.json()
	userId = str(jres["accessToken"]["userId"])
	userToken = str(jres["accessToken"]["id"])
	print("Logged into WEconnect system.")

	# Stores user's ID and access token in a JSON file
	jsonStr = '{"userId":"' + userId + '","userToken":"' + userToken + '"}'
	with open(filepath, "w+") as file:
		file.write(jsonStr)

# Checks if user is already logged into WEconnect
def isLoggedIn():
	text = ""
	if os.path.isfile(filepath):
		with open(filepath, "r") as file:
			file.seek(0)
			text = file.read()
		try:
			loginInfo = json.loads(text)

			# Only returns True if userId and userToken fields are filled
			if not loginInfo["userId"] or not loginInfo["userToken"]:
				return False
			else:
				return True

		# access.json is empty or doesn't contain valid JSON
		except:
			return False

	# access.json doesn't exist
	else:
		return False
