"""
module common\n
Functions and constants common to logmanager and usermanager\n
Created by Abigail Franz on 2/9/2018\n
Last modified by Abigail Franz on 2/16/2018
"""

from datetime import datetime

DB_PATH = "/export/scratch/ptdata/pt.db"

def _get_sqlite_timestamp():
	"""
	Get the current date and time in a format that Sqlite can understand.
	"""
	dt = datetime.now()
	formatted = format("%d-%02d-%02d %02d:%02d:%02d.000" 
				% (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second))
	return formatted
