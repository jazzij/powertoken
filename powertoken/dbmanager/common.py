# module dbmanager.common
# Functions and constants common to logmanager and usermanager
# Created by Abigail Franz on 2/9/2018
# Last modified by Abigail Franz on 2/10/2018

from datetime import datetime

DB_PATH = "/export/scratch/ptdata/pt.db"

# Helper - Gets the current date and time in a format that Sqlite can
# understand.
def _get_sqlite_timestamp():
	dt = datetime.now()
	formatted = format("%d-%02d-%02d %02d:%02d:%02d.000" 
				% (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second))
	return formatted
