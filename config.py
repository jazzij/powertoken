"""
Contains the configuration class for the Flask app.\n
Created by Abigail Franz on 3/12/2018.\n
Last modified by Abigail Franz on 5/9/2018.
"""

import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Retrieve the CSRF token from a file on the server. Make sure this file isn't
# world-readable! You can generate a good token with os.urandom(12) and then
# copy-paste it into the file called "csrf".
skey = ""
with open("csrf") as fp:
	skey = fp.read().strip()

# The environment variables are currently set in the run_powertoken.sh script.
# TODO: Add administrator email addresses to the ADMINS field.
class Config(object):
	"""
	Name-value pairs for the Flask app configuration.
	"""
	SECRET_KEY = os.environ.get("SECRET_KEY") or skey
	SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
		"sqlite:///" + os.path.join(basedir, "data/pt-fade.db")
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAIL_SERVER = os.environ.get("MAIL_SERVER")
	MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
	MAIL_USE_TLS = int(os.environ.get("MAIL_USE_TLS") or 0)
	MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
	MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
	ADMINS = ["franz322@umn.edu"]
	LOG_FILE = os.path.join(basedir, "data/app.log")