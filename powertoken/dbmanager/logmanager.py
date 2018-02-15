# module dbmanager.logmanager
# A non-class module to handle the logging portion of the application.
# Created by Abigail Franz on 2/9/2018
# Last modified by Abigail Franz on 2/10/2018

import sqlite3
from common import _get_sqlite_timestamp, DB_PATH

# Creates the "logs" table in the database if it doesn't already exist.
def create_logs_if_dne():
	query = ''' CREATE TABLE IF NOT EXISTS logs(
					id INTEGER PRIMARY KEY,
					timestamp TEXT NOT NULL,
					wc_progress REAL NOT NULL,
					fb_step_count INTEGER NOT NULL,
					user_id INTEGER NOT NULL, 
						FOREIGN KEY (user_id) REFERENCES users(id)) '''
	db = sqlite3.connect(DB_PATH)
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

# Adds a log to the database's "logs" table.
def insert_log(user_id, wc_progress, fb_step_count):
	timestamp = _get_sqlite_timestamp()
	query = ''' INSERT INTO logs(user_id, timestamp, wc_progress, fb_step_count)
				VALUES(?, ?, ?, ?) '''
	db = sqlite3.connect(DB_PATH)
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

# If no parameters are specified, returns all the logs in the database.
# If user_id is specified, returns all the logs for that user.
def get_logs(user_id=None):
	db = sqlite3.connect(DB_PATH)
	try:
		cursor = db.cursor()
		if user_id != None:
			query = ''' SELECT * FROM logs WHERE user_id=? '''
			cursor.execute(query, (user_id,))
		else:
			query = ''' SELECT * FROM logs '''
			cursor.execute(query)
		logs = cursor.fetchall()
		return logs
	except Exception as e:
		print(format("Couldn't retrieve logs. Message: %s" % (e,)))
		return None
	finally:
		db.close()
