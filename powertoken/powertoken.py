"""
module powertoken\n
Contains the functionality for interfacing between WEconnect and Fitbit\n
Created by Abigail Franz\n
Last modified by Abigail Franz on 2/16/2018
"""

import json, requests, time
import fitbit, weconnect
import dbmanager

class PowerToken:
	"""
	Main class of the PowerToken application.
	"""
	def __init__(self):
		dbmanager.create_logs_if_dne()
		dbmanager.create_users_if_dne()

	def is_current_user(self, username):
		"""
		Return True if the user has already been added.
		"""
		return dbmanager.user_exists(username)

	def create_user(self, username):
		"""
		Add a new PowerToken user, who will be referenced by a chosen username.
		"""
		dbmanager.insert_user(username)

	def login_to_wc(self, username, email, password, goal_period):
		"""
		Log user into WEconnect, produce an ID and access token that will last
		90 days, and store the token and ID. Also store the goal period.
		Return a Boolean indicating the success of the login.
		"""
		# Gets the ID and access token from the WEconnect server
		url = "https://palalinq.herokuapp.com/api/People/login"
		data = {"email": email, "password": password}
		result = requests.post(url, data=data)
		if result.status_code != 200:
			return False
		jres = result.json()
		wc_id = str(jres["accessToken"]["userId"])
		wc_token = str(jres["accessToken"]["id"])		

		# Stores user's WEconnect-related data in the db
		dbmanager.update_wc_info(username, goal_period, wc_id, wc_token)
		return True

	def is_logged_into_wc(self, username):
		"""
		Return a Boolean signifying that the user is or isn't logged into
		WEconnect.
		"""
		return dbmanager.wc_info_filled(username)

	def is_logged_into_fb(self, username):
		"""
		Return a Boolean value signifying that the user is or isn't logged
		into Fitbit.
		"""
		return dbmanager.fb_info_filled(username)

	def complete_fb_login(self, username, fb_token):
		"""
		Store the Fitbit access token.
		"""
		dbmanager.update_fb_info(username, fb_token)

	def start_experiment(self, username):
		"""
		The program loop. Run until killed with Ctrl+C.
		"""
		# Sets up the objects that will perform the WEconnect and Fitbit API
		# calls
		user = dbmanager.get_user(username)
		user_id = user["id"]
		wc = weconnect.WeConnect(user["wc_id"], user["wc_token"], user["goal_period"])
		fb = fitbit.Fitbit(user["fb_token"], user["goal_period"])

		# First, sets the Fitbit step goal to something ridiculous,
		# like a million steps
		fb.change_step_goal(1000000)

		# This will hold the progress from the last time WEconnect was polled.
		last_progress = 0.0

		# Starts an infinite loop that periodically polls WEconnect for changes
		# and then updates Fitbit. Progress will be a decimal percentage.
		while True:
			progress = wc.poll()

			# Makes sure the poll request succeeded
			if progress != -1:
				# If progress differs from last poll, updates Fitbit
				if progress != last_progress:
					step_count = fb.reset_and_update(progress)
					dbmanager.add_log(user_id, progress, step_count)
				last_progress = progress

			# Delays a minute
			time.sleep(60)
