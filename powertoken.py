"""
PowerToken Flask entry point.\n
Can be run from the command line with `flask run` or `python powertoken.py`. 
However, the preferred way of running the script is through Gunicorn, which
uses the script [wsgi.py](wsgi.py).\n
Created by Abigail Franz on 3/12/2018.\n
Last modified by jaztech on 1/2019.
"""

from app import create_app, db
from app.models import User, Admin, Log, Activity, Event, Day

app = create_app()


@app.shell_context_processor
def make_shell_context():
	return {
		"db": db,
		"User": User,
		"Admin": Admin,
		"Log": Log,
		"Activity": Activity,
		"Day": Day,
		"Event": Event
	}

if __name__ == "__main__":
	app.run(threaded=True)