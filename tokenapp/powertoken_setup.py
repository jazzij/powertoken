# powertoken_setup.py
# Contains the WEconnect login function

import requests

wcLoginUrl = "https://palalinq.herokuapp.com/api/People/login"

# Logs user into WEconnect and produces an access token that will last 90 days.
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
	with open("access.json", "w+") as file:
		file.write(jsonStr)
