# powertoken.py
# Contains the functionality for interfacing between WEconnect and Fitbit
# Created by Abigail Franz
# Last modified by Abigail Franz on 1/29/2018

import datetime, json, requests, sqlite3, time
import fitbit, weconnect

class PowerToken:
	_db_path = "data/ptdb"

	def __init__(self):
		self._create_table()

	# Returns True if the user has already been created
	def is_current_user(self, username):
		query = '''SELECT EXISTS(SELECT 1 FROM users WHERE username=? LIMIT 1);'''
		db = sqlite3.connect(self._db_path)
		cursor = db.cursor()
		if cursor.execute(query, (username,)) == 1:
			db.close()
			return True
		else:
			db.close()
			return False

	# Adds a new PowerToken user to the TinyDB. This user will be referenced by
	# a chosen username.
	def create_user(self, username):
		query = '''INSERT INTO users(username, registered_on) VALUES(?, ?)'''
		registered_on = datetime.datetime.now()
		db = sqlite3.connect(self._db_path)
		cursor = db.cursor()
		try:
			cursor.execute(query, (username, registered_on))
			db.commit()
		except expression as e:
			print("Error " + e)
		finally:
			db.close()

	# Logs user into WEconnect, produces an ID and access token that will last
	# 90 days, and stores the token and ID in the TinyDB. Also stores the goal
	# period. Returns True if the login is successful, false otherwise.
	def login_to_wc(self, username, email, password, goal_period):
		url = "https://palalinq.herokuapp.com/api/People/login"
		data = {
			"email": email,
			"password": password
		}
		result = requests.post(url, data=data)
		if result.status_code != 200:
			return False
		jres = result.json()
		wc_id = str(jres["accessToken"]["userId"])
		wc_token = str(jres["accessToken"]["id"])
		
		# Stores user's WEconnect-related data in the db
		query = '''UPDATE users SET goal_period=?, wc_id=?, wc_token=? WHERE username=?'''
		db = sqlite3.connect(self._db_path)
		cursor = db.cursor()
		cursor.execute(query, (goal_period, wc_id, wc_token, username))
		db.commit()
		db.close()
		#outputLogger.info(format(" The user %s was just logged into WEconnect." % (username,)))
		return True

	# Returns a boolean value signifying that the user is or isn't logged into 
	# WEconnect
	def is_logged_into_wc(self, username):
		query = '''SELECT wc_id, wc_token FROM users WHERE username=?'''
		db = sqlite3.connect(self._db_path)
		cursor = db.cursor()
		cursor.execute(query, (username,))
		results = cursor.fetchall()
		db.close()

		# Makes sure there exists a user with that username
		if len(results) != 1:
			return False
		else:
			# Only returns True if both WEconnect fields are filled
			user = results[0]
			if not user[0] or not user[1]:
				return False
			else:
				return True

	# Returns a boolean value signifying that the user is or isn't logged into
	# Fitbit
	def is_logged_into_fb(self, username):
		query = '''SELECT fb_token FROM users WHERE username=?;'''
		db = sqlite3.connect(self._db_path)
		cursor = db.cursor()
		cursor.execute(query, (username,))
		results = cursor.fetchall()
		db.close()

		# Makes sure there exists a user with that username
		if len(results) != 1:
			return False
		else:
			# Only returns True if the Fitbit access token field is filled
			user = results[0]
			if not user[0]:
				return False
			else:
				return True

	# Stores the Fitbit access token in the database
	def complete_fb_login(self, username, accessToken):
		query = '''UPDATE users SET fb_token=? WHERE username=?'''
		db = sqlite3.connect(self._db_path)
		cursor = db.cursor()
		cursor.execute(query, (username,))
		db.commit()
		db.close()

	# The program loop - runs until killed with Ctrl+C
	def start_experiment(self, username):
		# Sets up the objects that will perform the WEconnect and Fitbit API
		# calls
		goal_period, wc_id, wc_token, fb_token = self._load_info(username)
		wc = weconnect.WeConnect(wc_id, wc_token, goal_period)
		fb = fitbit.Fitbit(fb_token, goal_period)

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
				last_progress = progress
				
				'''logEntry = {
					"username": username,
					"wcProgress": wcProgress,
					"fbStepCount": fbStepCount,
					"timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
				}
				self._log.insert(logEntry)'''

			# Delays a minute
			time.sleep(60)

	# Helper - creates a table to store the users in the database, provided one
	# does not already exist.
	def _create_table(self):
		query = '''	CREATE TABLE IF NOT EXISTS users (
						id INTEGER PRIMARY KEY,
						username TEXT NOT NULL UNIQUE,
						registered_ON TEXT,
						goal_period TEXT NOT NULL DEFAULT "daily",
						wc_id TEXT,
						wc_token TEXT,
						fb_token TEXT
				); '''
		db = sqlite3.connect(self._db_path)
		cursor = db.cursor()
		cursor.execute(query)
		db.commit()
		db.close()

	# Helper - retrieves user's info from the database.
	def _load_info(self, username):
		query = ''' SELECT goal_period, wc_id, wc_token, fb_token
					FROM users
					WHERE username=? '''
		db = sqlite3.connect(self._db_path)
		cursor = db.cursor()
		cursor.execute(query, (username,))
		user = cursor.fetchone()
		db.close()
		return user[0], user[1], user[2], user[3]
