"""
Contains the configuration class for the Flask app.\n
Created by Abigail Franz on 3/12/2018.\n
Last modified by Abigail Franz on 5/9/2018.
"""

import os

basedir = os.path.abspath(os.path.curdir)

# The environment variables are currently set in the run_powertoken.sh script.
# TODO: Add administrator email addresses to the ADMINS field.
class Config(object):
	"""
	Name-value pairs for the Flask app configuration.
	"""
	SECRET_KEY = os.environ.get("SECRET_KEY")
	SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
		"sqlite:///" + os.path.join(basedir, "data/pt-fade.db")
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAIL_SERVER = os.environ.get("MAIL_SERVER")
	MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
	MAIL_USE_TLS = int(os.environ.get("MAIL_USE_TLS") or 0)
	MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
	MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
	ADMINS = ["franz322@umn.edu"]
	LOG_FILE = os.environ.get("LOG_PATH") or \
		os.path.join(basedir, "data/app.log")