# powertoken.py
# Contains the functionality for interfacing between WEconnect and Fitbit
# Created by Abigail Franz
# Last modified by Abigail Franz on 2/9/2018

import datetime, json, requests, sqlite3, time
import fitbit, weconnect
import dbmanager

class PowerToken:
	_db_path = "data/ptdb"

	def __init__(self):
		dbmanager.create_logs_if_dne()
		dbmanager.create_users_if_dne()

	# Returns True if the user has already been created
	def is_current_user(self, username):
		return dbmanager.user_exists(username)

	# Adds a new PowerToken user to the database. This user will be referenced
	# by a chosen username.
	def create_user(self, username):
		dbmanager.insert_user(username)

	# Logs user into WEconnect, produces an ID and access token that will last
	# 90 days, and stores the token and ID in the database. Also stores the goal
	# period. Returns True if the login is successful, False otherwise.
	def login_to_wc(self, username, email, password, goal_period):
		# Gets the ID and access token from the WEconnect server
		url = "https://palalinq.herokuapp.com/api/People/login"
		data = {"email": email, "password": password}
		result = requests.post(url, data=data)
		if result.status_code >= 400:
			return False
		jres = result.json()
		wc_id = str(jres["accessToken"]["userId"])
		wc_token = str(jres["accessToken"]["id"])
		
		# Stores user's WEconnect-related data in the db
		dbmanager.update_wc_info(username, goal_period, wc_id, wc_token)

	# Returns a boolean value signifying that the user is or isn't logged into 
	# WEconnect
	def is_logged_into_wc(self, username):
		return dbmanager.wc_info_filled(username)

	# Returns a boolean value signifying that the user is or isn't logged into
	# Fitbit
	def is_logged_into_fb(self, username):
		return dbmanager.fb_info_filled(username)

	# Stores the Fitbit access token in the database
	def complete_fb_login(self, username, fb_token):
		dbmanager.update_fb_info(username, fb_token)

	# The program loop - Runs until killed with Ctrl+C
	def start_experiment(self, username):
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
					dbmanager.insert_log(user_id, progress, step_count)
				last_progress = progress

			# Delays a minute
			time.sleep(60)