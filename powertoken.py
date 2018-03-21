"""
PowerToken Flask entry point.\n
Can be run from the command line with "flask run" or "python powertoken".\n
Created by Abigail Franz on 3/12/2018\n
Last modified by Abigail Franz on 3/13/2018
"""

from app import app, db
from app.models import User, Admin, Log, Activity

@app.shell_context_processor
def make_shell_context():
	return {
		"db": db,
		"User": User,
		"Admin": Admin,
		"Log": Log,
		"Activity": Activity
	}

if __name__ == "__main__":
	app.run(debug=True, threaded=True)