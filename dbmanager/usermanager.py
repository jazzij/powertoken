# module dbmanager.usermanager
# A non-class module to deal with the "users" table in the database
# Created by Abigail Franz on 2/9/2018
# Last modified by Abigail Franz on 2/10/2018

import sqlite3
from common import _get_sqlite_timestamp, DB_PATH

def create_users_if_dne():
	query = '''CREATE TABLE IF NOT EXISTS users(
					id INTEGER PRIMARY KEY,
					username TEXT NOT NULL UNIQUE, 
					registered_on TEXT,
					goal_period TEXT NOT NULL DEFAULT "daily",
					wc_id TEXT,
					wc_token TEXT,
					fb_token TEXT)'''
	db = sqlite3.connect(DB_PATH)
	try:
		cursor = db.cursor()
		cursor.execute(query)
		db.commit()
	except Exception as e:
		db.rollback()
		print(format("Couldn't create table users. Message: %s" % (e,)))
	finally:
		db.close()

def user_exists(username):
	db = sqlite3.connect(DB_PATH)
	try:
		cursor = db.cursor()
		query = '''SELECT * FROM users WHERE username=? LIMIT 1'''
		cursor.execute(query, (username,))
		user = cursor.fetchone()
		if user == None:
			return False
		else:
			return True
	except Exception as e:
		print(format("Couldn't determine if user exists. Message: %s" % (e,)))
		return None
	finally:
		db.close()

def insert_user(username):
	db = sqlite3.connect(DB_PATH)
	try:
		cursor = db.cursor()
		query = '''INSERT INTO users(username, registered_on) VALUES(?, ?)'''
		registered_on = _get_sqlite_timestamp()
		cursor.execute(query, (username, registered_on))
		db.commit()
		return True
	except Exception as e:
		db.rollback()
		print(format("Could not add user to the db. Message: %s" % (e),))
		return False
	finally:
		db.close()

def update_wc_info(username, goal_period, wc_id, wc_token):
	db = sqlite3.connect(DB_PATH)
	try:
		cursor = db.cursor()
		query = '''UPDATE users SET goal_period=?, wc_id=?, wc_token=? WHERE username=?'''
		cursor.execute(query, (goal_period, wc_id, wc_token, username))
		db.commit()
		return True
	except Exception as e:
		db.rollback()
		print("Could not add wc info. Message: %s" % (e,))
		return False
	finally:
		db.close()

def wc_info_filled(username):
	db = sqlite3.connect(DB_PATH)
	try:
		db.row_factory = sqlite3.Row
		cursor = db.cursor()
		query = '''SELECT wc_id, wc_token FROM users WHERE username=?'''
		cursor.execute(query, (username,))
		user = cursor.fetchone()
			
		# Only returns True if both WEconnect fields are filled
		if (user["wc_id"] == None) or (user["wc_token"] == None):
			print("User is not logged into WEconnect")
			return False
		else:
			print("User is logged into WEconnect")
			return True
	except Exception as e:
		print("Couldn't find user's wc login status. Message: %s" % (e,))
		return None
	finally:
		db.close()

def fb_info_filled(username):
	db = sqlite3.connect(DB_PATH)
	try:
		db.row_factory = sqlite3.Row
		cursor = db.cursor()
		query = '''SELECT fb_token FROM users WHERE username=?'''
		cursor.execute(query, (username,))
		user = cursor.fetchone()
			
		# Only returns True if the Fitbit access token field is filled
		if user["fb_token"] == None:
			print("User is not logged into Fitbit")
			return False
		else:
			print("User is logged into Fitbit")
			return True
	except Exception as e:
		print("Couldn't find user's fb login status. Message: " % (e,))
	finally:
		db.close()

def update_fb_info(username, fb_token):
	db = sqlite3.connect(DB_PATH)
	try:
		cursor = db.cursor()
		query = ''' UPDATE users SET fb_token=? WHERE username=? '''
		cursor.execute(query, (fb_token, username,))
		db.commit()
		print("Successfully stored fb token in db. fb_token = " + access_token)
	except Exception as e:
		db.rollback()
		print(format("Couldn't add Fitbit token to the db. Message: %s" % (e,)))
	finally:
		db.close()

# Returns all the users in the database
def get_users():
	db = sqlite3.connect(DB_PATH)
	try:
		cursor = db.cursor()
		query = ''' SELECT * FROM users '''
		cursor.execute(query)
		users = cursor.fetchall()
		return users
	except Exception as e:
		print(format("Couldn't retrieve users. Message: %s" % (e,)))
		return None
	finally:
		db.close()

# Returns a single user, specified by username or id
def get_user(username=None, id=None):
	db = sqlite3.connect(DB_PATH)
	try:
		db.row_factory = sqlite3.Row
		cursor = db.cursor()
		if username != None:
			query = ''' SELECT * FROM users WHERE username=? '''
			cursor.execute(query, (username,))
		elif id != None:
			query = ''' SELECT * FROM users WHERE id=? '''
			cursor.execute(query, (id,))
		else:
			raise(Exception())
		user = cursor.fetchone()
		return user
	except Exception as e:
		print(format("Couldn't retrieve users. Message: %s" % (e,)))
		return None
	finally:
		db.close()