"""
Contains the configuration class for the Flask app.\n
Created by Abigail Franz on 3/12/2018\n
Last modified by Abigail Franz on 3/25/2018
"""

import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Retrieve the CSRF token
skey = ""
with open("csrf") as fp:
	skey = fp.read().strip()

class Config(object):
	"""
	Name-value pairs for the Flask app configuration.
	"""
	SECRET_KEY = os.environ.get("SECRET_KEY") or skey
	SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
		"sqlite:///" + os.path.join(basedir, "data/pt.db")
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAIL_SERVER = os.environ.get("MAIL_SERVER")
	MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
	MAIL_USE_TLS = os.environ.get("MAIL_USERNAME")
	MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
	ADMINS = ["franz322@umn.edu"] # Should eventually add Jasmine