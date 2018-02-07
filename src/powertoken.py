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
		try:
			db = sqlite3.connect(self._db_path)
			cursor = db.cursor()
			query = "SELECT * FROM users WHERE username=? LIMIT 1"
			cursor.execute(query, (username,))
			user = cursor.fetchone()
			if user == None:
				return False
			else:
				return True
		except Exception as e:
			print(format("Couldn't determine if user exists. Message: %s" % (e,)))
			raise(e)
		finally:
			db.close()

	# Adds a new PowerToken user to the database. This user will be referenced
	# by a chosen username.
	def create_user(self, username):
		try:
			db = sqlite3.connect(self._db_path)
			cursor = db.cursor()
			query = '''INSERT INTO users(username, registered_on) VALUES(?, ?)'''
			registered_on = datetime.datetime.now()
			cursor.execute(query, (username, registered_on))
			db.commit()
			query = "SELECT * FROM users ORDER BY id DESC LIMIT 1"
			cursor.execute(query)
			print("User just inserted: " + cursor.fetchone())
		except Exception as e:
			db.rollback()
			print(format("Could not add user to the db. Message: %s" % (e,)))
			raise(e)
		finally:
			db.close()

	# Logs user into WEconnect, produces an ID and access token that will last
	# 90 days, and stores the token and ID in the database. Also stores the goal
	# period. Returns True if the login is successful, False otherwise.
	def login_to_wc(self, username, email, password, goal_period):
		# Gets the ID and access token from WEconnect server
		url = "https://palalinq.herokuapp.com/api/People/login"
		data = {"email": email, "password": password}
		result = requests.post(url, data=data)
		if result.status_code != 200:
			return False
		jres = result.json()
		wc_id = str(jres["accessToken"]["userId"])
		wc_token = str(jres["accessToken"]["id"])
		
		# Stores user's WEconnect-related data in the db
		try:
			db = sqlite3.connect(self._db_path)
			cursor = db.cursor()
			query = '''UPDATE users SET goal_period=?, wc_id=?, wc_token=? WHERE username=?'''
			cursor.execute(query, (goal_period, wc_id, wc_token, username))
			db.commit()
			print("Successfully logged into WEconnect. Id = " + wc_id + ", token = " + wc_token)
			return True
		except Exception as e:
			db.rollback()
			print(format("Could not add wc info to user's record. Message: %s" % (e,)))
			raise(e)
		finally:
			db.close()

	# Returns a boolean value signifying that the user is or isn't logged into 
	# WEconnect
	def is_logged_into_wc(self, username):
		try:
			db = sqlite3.connect(self._db_path)
			cursor = db.cursor()
			query = '''SELECT wc_id, wc_token FROM users WHERE username=?'''
			cursor.execute(query, (username,))
			results = cursor.fetchall()

			# Makes sure there exists a user with that username
			if len(results) != 1:
				return False
			
			# Only returns True if both WEconnect fields are filled
			print("results = " + results)
			user = results[0]
			if not user[0] or not user[1]:
				return False
			else:
				print(format("User is logged into WEconnect"))
				return True
		except Exception as e:
			print("Couldn't find user's wc login status. Message: " % (e,))
			raise(e)
		finally:
			db.close()

	# Returns a boolean value signifying that the user is or isn't logged into
	# Fitbit
	def is_logged_into_fb(self, username):
		try:
			db = sqlite3.connect(self._db_path)
			cursor = db.cursor()
			query = '''SELECT fb_token FROM users WHERE username=?;'''
			cursor.execute(query, (username,))
			results = cursor.fetchall()

			# Makes sure there exists a user with that username
			print("results = " + results)
			if len(results) != 1:
				return False
			
			# Only returns True if the Fitbit access token field is filled
			user = results[0]
			if not user[0]:
				return False
			else:
				return True
		except Exception as e:
			print("Couldn't find user's fb login status. Message: " % (e,))
			raise(e)
		finally:
			db.close()

	# Stores the Fitbit access token in the database
	def complete_fb_login(self, username, access_token):
		query = '''UPDATE users SET fb_token=? WHERE username=?'''
		try:
			db = sqlite3.connect(self._db_path)
			cursor = db.cursor()
			cursor.execute(query, (access_token, username,))
			db.commit()
			print("Successfully stored fb token in db. fb_token = " + access_token)
		except Exception as e:
			db.rollback()
			print(format("Couldn't add Fitbit token to the db. Message: %s" % (e,)))
			raise(e)
		finally:
			db.close()

	# The program loop - Runs until killed with Ctrl+C
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

	# Helper - Creates a table to store the users in the database, provided one
	# does not already exist.
	def _create_table(self):
		query = '''CREATE TABLE IF NOT EXISTS users(
					id INTEGER PRIMARY KEY,
					username TEXT NOT NULL UNIQUE, 
					registered_ON TEXT,
					goal_period TEXT NOT NULL DEFAULT "daily",
					wc_id TEXT,
					wc_token TEXT,
					fb_token TEXT);'''
		try:
			db = sqlite3.connect(self._db_path)
			cursor = db.cursor()
			cursor.execute(query)
			db.commit()
			print("Successfully created table users.")
		except Exception as e:
			db.rollback()
			print(format("Couldn't create table users. Message: %s" % (e,)))
			raise(e)
		finally:
			db.close()

	# Helper - Retrieves user's info from the database.
	def _load_info(self, username):
		try:
			db = sqlite3.connect(self._db_path)
			cursor = db.cursor()
			query = '''SELECT goal_period, wc_id, wc_token, fb_token
				FROM users WHERE username=?'''
			cursor.execute(query, (username,))
			user = cursor.fetchone()
			print("user fetched: " + user)
			return user[0], user[1], user[2], user[3]
		except Exception as e:
			print(format("Couldn't load user info. Message: %s" % (e,)))
			raise(e)
		finally:
			db.close()
