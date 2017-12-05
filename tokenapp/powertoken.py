# powertoken.py
# Contains the necessary functions for interfacing between WEconnect and Fitbit

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

	# Returns a boolean value signifying that the user is or isn't logged into 
	# WEconnect
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

			# wc.json is empty or doesn't contain valid JSON
			except:
				return False

		# wc.json doesn't exist
		else:
			return False

	# Returns a boolean value signifying that the user is or isn't logged into
	# Fitbit.
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

	# TODO: Debug this code
	def startExperiment(self):
		wc = weconnect.WeConnect()
		fb = fitbit.Fitbit()

		# First, sets the Fitbit daily step goal to something ridiculous -
		# like a million steps
		fb.changeDailyStepGoal(1000000)

		lastWcProgress = 0.0

		# Starts an infinite loop that periodically polls WEconnect for changes
		# and then updates Fitbit
		while True:
			wcProgress = wc.poll() # wcProgress will be a percentage
			if wcProgress > lastWcProgress:
				fb.update(wcProgress - lastWcProgress)
			lastWcProgress = wcProgress
			time.sleep(60)





