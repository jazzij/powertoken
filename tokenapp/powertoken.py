# powertoken.py
# Contains the necessary functions for interfacing between WEconnect and Fitbit

import json, os, requests, time, fitbit, weconnect
from tinydb import TinyDB, Query

class PowerToken:
	wcLoginUrl = "https://palalinq.herokuapp.com/api/People/login"
	wcAccessFile = "data/wc.json"
	fbAccessFile = "data/fb.json"
	dbPath = "data/db.json"
	db = TinyDB(dbPath)

	# Logs user into WEconnect and produces an access token that will last 90 days
	def loginToWc_old(self, email, password):
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

	# New version of the function that makes use of tinydb
	def loginToWc(self, email, password):
		result = requests.post(self.wcLoginUrl, data={"email":email, "password":password})
		if result.status_code != 200:
			print("Login error")
			exit()
		jres = result.json()
		userId = str(jres["accessToken"]["userId"])
		userToken = str(jres["accessToken"]["id"])
		print("Logged into WEconnect system.")

		# Stores user's WEconnect-related data in the tinydb
		self.db.insert({"email":email, "wcUserId":userId, "wcAccessToken":userToken, "fbAccessToken":""})

	# Returns a boolean value signifying that the user is or isn't logged into 
	# WEconnect
	def isLoggedIntoWc_old(self, email):
		text = ""
		if os.path.isfile(self.wcAccessFile):
			with open(self.wcAccessFile, "r") as file:
				file.seek(0)
				text = file.read()
			try:
				loginInfo = json.loads(text)

				# Only returns True if userId and userToken fields are filled
				if not loginInfo["wcUserId"] or not loginInfo["wcUserToken"]:
					return False
				else:
					return True

			# wc.json is empty or doesn't contain valid JSON
			except:
				return False

		# wc.json doesn't exist
		else:
			return False

	# New version that makes use of tinydb
	def isLoggedIntoWc(self, email):
		user = Query()
		result = self.db.search(user.email == email)
		# Makes sure there exists a user with that email
		if len(result) != 1:
			return False
		else:
			# Only returns True if both WEconnect fields are filled
			if not result[0]["wcUserId"] or not result[0]["wcAccessToken"]:
				return False;
			else:
				return True

	# Returns a boolean value signifying that the user is or isn't logged into
	# Fitbit.
	def isLoggedIntoFb_old(self):
		text = ""
		if os.path.isfile(self.fbAccessFile):
			print("fb.json exists")
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
				print("but fb.json is empty or contains invalid JSON")
				return False

		# fb.json doesn't exist
		else:
			print("fb.json doesn't exist")
			return False

	# New version that uses TinyDB
	def isLoggedIntoFb(self, email):
		user = Query()
		result = self.db.search(user.email == email)
		# Makes sure there exists a user with that email
		if len(result) != 1:
			return False
		else:
			# Only returns True if the Fitbit access token field is filled
			if not result[0]["fbAccessToken"]:
				return False;
			else:
				return True

	def completeFbLogin(self, email, accessToken):
		user = Query()
		self.db.update({"fbAccessToken": accessToken}, user.email == email)
		return

	# TODO: Debug this code
	def startExperiment_old(self):
		wc = weconnect.WeConnect(email)
		fb = fitbit.Fitbit(email)

		# First, sets the Fitbit daily step goal to something ridiculous -
		# like a million steps
		fb.changeWeeklyStepGoal(1000000)

		lastWcProgress = 0.0

		# Starts an infinite loop that periodically polls WEconnect for changes
		# and then updates Fitbit
		while True:
			wcProgress = wc.poll() # wcProgress will be a percentage
			if wcProgress != lastWcProgress:
				fb.update(wcProgress - lastWcProgress)
			lastWcProgress = wcProgress
			time.sleep(60)

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
			elif wcProgress < lastWcProgress:
				fb.resetAndUpdate(wcProgress)
			lastWcProgress = wcProgress
			time.sleep(60)

	def runTests(self):
		wc = weconnect.WeConnect()
		fb = fitbit.Fitbit()
		response = fb.resetAndUpdate(0.5)
		#response = fb.changeDailyStepGoal(1000000)
		#print(response)
		#response = fb.logStepActivity(250000);
		#print(response)