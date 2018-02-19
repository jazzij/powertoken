""" 
module logmanager\n
A non-class module to handle the logging portion of the application.\n
Created by Abigail Franz on 2/9/2018\n
Last modified by Abigail Franz on 2/16/2018
"""

import sqlite3
from common import _get_sqlite_timestamp, DB_PATH

# Creates the "logs" table in the database if it doesn't already exist.
def create_logs_if_dne():
	"""
	Create the logs table in the database if it does not already exist. Return
	Boolean indicating success.
	"""
	query = ''' CREATE TABLE IF NOT EXISTS logs(
					id INTEGER PRIMARY KEY,
					timestamp TEXT NOT NULL,
					wc_progress REAL NOT NULL,
					fb_step_count INTEGER NOT NULL,
					user_id INTEGER NOT NULL, 
						FOREIGN KEY (user_id) REFERENCES users(id)) '''
	db = sqlite3.connect(DB_PATH)
	db.row_factory = sqlite3.Row
	try:
		cursor = db.cursor()
		cursor.execute(query)
		db.commit()
		return True
	except Exception as e:
		db.rollback()
		print(format("Couldn't create table logs. Message: %s" % (e,)))
		return False
	finally:
		db.close()

def insert_log(user_id, wc_progress, fb_step_count):
	"""
	Insert a new log row into the database. Return Boolean indicating success.
	"""
	timestamp = _get_sqlite_timestamp()
	query = ''' INSERT INTO logs(user_id, timestamp, wc_progress, fb_step_count)
				VALUES(?, ?, ?, ?) '''
	db = sqlite3.connect(DB_PATH)
	db.row_factory = sqlite3.Row
	try:
		cursor = db.cursor()
		cursor.execute(query, (user_id, timestamp, wc_progress, fb_step_count))
		db.commit()
		return True
	except Exception as e:
		db.rollback()
		print(format("Couldn't add log. Message: %s" % (e,)))
		return False
	finally:
		db.close()

def get_logs(user_id=None):
	"""
	If no parameters are specified, return all the logs in the database. If
	user_id is specified, return all the logs for that user.
	"""
	db = sqlite3.connect(DB_PATH)
	db.row_factory = sqlite3.Row
	try:
		cursor = db.cursor()
		if user_id != None:
			query = '''SELECT * FROM logs WHERE user_id=?'''
			cursor.execute(query, (user_id,))
		else:
			query = '''SELECT * FROM logs'''
			cursor.execute(query)
		logs = cursor.fetchall()
		return logs
	except Exception as e:
		print(format("Couldn't retrieve logs. Message: %s" % (e,)))
		return []
	finally:
		db.close()