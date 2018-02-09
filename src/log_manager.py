# log_manager.py
# A non-class module to handle the logging portion of the application.
# Created by Abigail Franz on 2/9/2018

import datetime, sqlite3

_db_path = "data/ptdb"

# Creates the "logs" table in the database if it doesn't already exist.
def create_table_if_dne():
	query = ''' CREATE TABLE IF NOT EXISTS logs(
				id INTEGER PRIMARY KEY,
				timestamp TEXT NOT NULL,
				wc_progress REAL NOT NULL,
				fb_step_count INTEGER NOT NULL,
				user_id INTEGER NOT NULL, 
					FOREIGN KEY (user_id) REFERENCES users(id)) '''
	try:
		db = sqlite3.connect(_db_path)
		cursor = db.cursor()
		cursor.execute(query)
		db.commit()
	except Exception as e:
		db.rollback()
		print(format("Couldn't create table logs. Message: %s" % (e,)))
		#raise(e)
	finally:
		db.close()

# Adds a log to the database's "logs" table.
def add_log(user_id, wc_progress, fb_step_count):
	timestamp = _get_sqlite_timestamp()
	query = ''' INSERT INTO logs(user_id, timestamp, wc_progress, fb_step_count)
				VALUES(?, ?, ?, ?) '''
	try:
		db = sqlite3.connect(_db_path)
		cursor = db.cursor()
		cursor.execute(query, (user_id, timestamp, wc_progress, fb_step_count))
		db.commit()
	except Exception as e:
		db.rollback()
		print(format("Couldn't add log. Message: %s" % (e,)))
	finally:
		db.close()

# Returns all the logs in the database
def get_logs():
	query = ''' SELECT * FROM logs '''
	try:
		db = sqlite3.connect(_db_path)
		cursor = db.cursor()
		cursor.execute(query)
		logs = cursor.fetchall()
		return logs
	except Exception as e:
		print(format("Couldn't retrieve logs. Message: %s" % (e,)))
		return ()
	finally:
		db.close()
	

# Helper - Gets the current date and time in a format that Sqlite can
# understand.
def _get_sqlite_timestamp():
	dt = datetime.datetime.now()
	formatted = format("%d-%02d-%02d %02d:%02d:%02d.000" 
				% (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second))
	return formatted