# powertoken.py
# Contains the functionality for interfacing between WEconnect and Fitbit
# Created by: Abigail Franz
# Last modified by: Abigail Franz on 1/24/2018

import json, requests, time
from tinydb import TinyDB, Query
import fitbit, weconnect

class PowerToken:
	wcLoginUrl = "https://palalinq.herokuapp.com/api/People/login"
	_dbPath = "db.json"
	_db = TinyDB(_dbPath)

	# This will clear all user info and should only be called if you know what you're doing!
	# We will remove this function eventually.
	def resetLogins(self):
		self._db.purge()

	# Returns True if the user has already been created
	def isCurrentUser(self, username):
		q = Query()
		result = self._db.search(q.username == username)
		if len(result) == 1:
			return True
		else:
			return False

	# Adds a new PowerToken user to the TinyDB. This user will be referenced by
	# a chosen username.
	def createUser(self, username):
		newUser = {
			"username": username,
			"goalPeriod": "",
			"wcUserId": "",
			"wcAccessToken": "",
			"fbAccessToken": ""
		}
		self._db.insert(newUser)

	# Logs user into WEconnect, produces an ID and access token that will last
	# 90 days, and stores the token and ID in the TinyDB. Also stores the goal
	# period. Returns True if the login is successful, false otherwise.
	def loginToWc(self, username, email, password, goalPeriod):
		data = {
			"email": email,
			"password": password
		}
		result = requests.post(self.wcLoginUrl, data=data)
		if result.status_code != 200:
			return False
		jres = result.json()
		userId = str(jres["accessToken"]["userId"])
		userToken = str(jres["accessToken"]["id"])
		
		# Stores user's WEconnect-related data in the TinyDb
		userInfo = {
			"goalPeriod": goalPeriod,
			"wcUserId": userId,
			"wcAccessToken": userToken
		}
		q = Query()
		self._db.update(userInfo, q.username == username)
		return True

	# Returns a boolean value signifying that the user is or isn't logged into 
	# WEconnect
	def isLoggedIntoWc(self, username):
		q = Query()
		result = self._db.search(q.username == username)

		# Makes sure there exists a user with that username
		if len(result) != 1:
			return False
		else:
			# Only returns True if both WEconnect fields are filled
			user = result[0]
			if not user["wcUserId"] or not user["wcAccessToken"]:
				return False
			else:
				return True

	# Returns a boolean value signifying that the user is or isn't logged into
	# Fitbit
	def isLoggedIntoFb(self, username):
		q = Query()
		result = self._db.search(q.username == username)

		# Makes sure there exists a user with that username
		if len(result) != 1:
			return False
		else:
			# Only returns True if the Fitbit access token field is filled
			user = result[0]
			if not user["fbAccessToken"]:
				return False
			else:
				return True

	# Stores the Fitbit access token in the TinyDB
	def completeFbLogin(self, username, accessToken):
		q = Query()
		self._db.update({"fbAccessToken": accessToken}, q.username == username)
		result = self._db.search(q.username == username)

	# The program loop - runs until killed with Ctrl+C
	def startExperiment_old(self, username):
		# Sets up the objects that will perform the WEconnect and Fitbit API
		# calls
		wcUserId, wcAccessToken, fbAccessToken = self._loadAccessInfo(username)
		wc = weconnect.WeConnect(wcUserId, wcAccessToken)
		fb = fitbit.Fitbit(fbAccessToken)

		# First, sets the Fitbit daily step goal to something ridiculous,
		# like a million steps
		fb.changeDailyStepGoal(1000000)

		# This will hold the progress from the last time WEconnect was polled.
		lastWcProgress = 0.0

		# Starts an infinite loop that periodically polls WEconnect for changes
		# and then updates Fitbit. wcProgess will be a decimal percentage.
		while True:
			wcProgress = wc.poll()

			# If the user has made progress, adds to Fitbit step count
			if wcProgress > lastWcProgress:
				fb.update(wcProgress - lastWcProgress)

			# If the user's progress has decreased (i.e. by adding more
			# activities), subtracts from the Fitbit step count
			elif wcProgress < lastWcProgress:
				fb.resetAndUpdate(wcProgress)

			lastWcProgress = wcProgress
			time.sleep(60)

	# The program loop - runs until killed with Ctrl+C
	def startExperiment(self, username):
		# Sets up the objects that will perform the WEconnect and Fitbit API
		# calls
		userInfo = self._loadAccessInfo(username)
		wc = weconnect.WeConnect(userInfo["wcUserId"], userInfo["wcAccessToken"],
				userInfo["goalPeriod"])
		fb = fitbit.Fitbit(fbAccessToken, userInfo["goalPeriod"])

		# First, sets the Fitbit step goal to something ridiculous,
		# like a million steps
		fb.changeStepGoal(1000000)

		# This will hold the progress from the last time WEconnect was polled.
		lastWcProgress = 0.0

		# Starts an infinite loop that periodically polls WEconnect for changes
		# and then updates Fitbit. Progress will be a decimal percentage.
		while True:
			wcProgress = wc.poll()

			# Makes sure the poll request succeeded
			if wcProgress != -1:
				# If progress differs from last poll, updates Fitbit
				if wcProgress != lastWcProgress:
					fb.resetAndUpdate(wcProgress)
				lastWcProgress = wcProgress

			# Delays a minute
			time.sleep(60)

	# Helper - retrieves user's info from the TinyDB
	def _loadAccessInfo(self, username):
		q = Query()
		return self._db.search(q.username == username)[0]
