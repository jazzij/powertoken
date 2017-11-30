# powertoken.py
# Contains the WEconnect login function

import json, os, requests, time, fitbit, weconnect

class PowerToken:
	wcLoginUrl = "https://palalinq.herokuapp.com/api/People/login"
	wcAccessFile = "data/wc.json"
	fbAccessFile = "data/fb.json"

	# Logs user into WEconnect and produces an access token that will last 90 days
	def loginToWc(self, email, password):
		result = requests.post(self.wcLoginUrl, data={"email":email, "password":password})
		if result.status_code != 200:
			print("Login error")
			exit()
		jres = result.json()
		userId = str(jres["accessToken"]["userId"])
		userToken = str(jres["accessToken"]["id"])
		print("Logged into WEconnect system.")

		# Stores user's ID and access token in a JSON file
		jsonStr = '{"userId":"' + userId + '","userToken":"' + userToken + '"}'
		with open(self.wcAccessFile, "w+") as file:
			file.write(jsonStr)

	# Checks if user is already logged into WEconnect
	def isLoggedIntoWc(self):
		text = ""
		if os.path.isfile(self.wcAccessFile):
			with open(self.wcAccessFile, "r") as file:
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

	def isLoggedIntoFb(self):
		text = ""
		if os.path.isfile(self.fbAccessFile):
			with open(self.fbAccessFile, "r") as file:
				file.seek(0)
				text = file.read()
			try:
				loginInfo = json.loads(text)

				# Only returns True if userToken field is filled
				if not loginInfo["userToken"]:
					return False
				else:
					return True

			# fb.json is empty or doesn't contain valid JSON
			except:
				return False

		# fb.json doesn't exist
		else:
			return False

	# TODO: Test this code
	def startExperiment(self):
		wc = weconnect.WeConnect()
		fb = fitbit.Fitbit()
		while True:
			time.sleep(60)
			wcProgress = wc.poll() # wcProgress will be a percentage
			fb.update(wcProgress)





