"""
Initializes the PowerToken Flask app variables.\n
Created by Abigail Franz on 3/12/2018.\n
Last modified by Abigail Franz on 3/13/2018.
"""

import os.path
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

#from powertoken.models import db


#app = Flask(__name__)
#app.config.from_object(Config)
db = SQLAlchemy()
#db.init_app(app)
migrate = Migrate()
login = LoginManager()
login.login_view = "admin_login"

''' DELETE, moved to create_app
# Set up email logging for system failures.
if not app.debug:
	# Configure email logging
	if app.config["MAIL_SERVER"]:
		auth = None
		if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
			auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
		secure = None
		if app.config["MAIL_USE_TLS"]:
			secure = ()
		mail_handler = SMTPHandler(
			mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
			fromaddr="no-replay@" + app.config["MAIL_SERVER"],
			toaddrs=app.config["ADMINS"],
			subject="PowerToken Flask Failure",
			credentials=auth,
			secure=secure
		)
		mail_handler.setLevel(logging.ERROR)
		app.logger.addHandler(mail_handler)

	# Configure file logging
	file_handler = RotatingFileHandler(app.config["LOG_FILE"], maxBytes=10240,
		backupCount=20)
	file_handler.setFormatter(logging.Formatter(
		"%(asctime)s %(levelname)4s: %(message)s [in %(pathname)s:%(lineno)d]"))
	file_handler.setLevel(logging.WARNING)
	app.logger.addHandler(file_handler)
'''	
def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(config_class)
	db.init_app(app)
	migrate.init_app(app, db)
	login.init_app(app)
	
	# Set up email logging for system failures.
	if not app.debug:
		# Configure email logging
		if app.config["MAIL_SERVER"]:
			auth = None
			if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
				auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
			secure = None
			if app.config["MAIL_USE_TLS"]:
				secure = ()
			mail_handler = SMTPHandler(
				mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
				fromaddr="no-replay@" + app.config["MAIL_SERVER"],
				toaddrs=app.config["ADMINS"],
				subject="PowerToken Flask Failure",
				credentials=auth,
				secure=secure)
			mail_handler.setLevel(logging.ERROR)
			app.logger.addHandler(mail_handler)

		# Configure file logging
		file_handler = RotatingFileHandler(app.config["LOG_FILE"], maxBytes=10240,
			backupCount=20)
		file_handler.setFormatter(logging.Formatter(
			"%(asctime)s %(levelname)4s: %(message)s [in %(pathname)s:%(lineno)d]"))
		file_handler.setLevel(logging.WARNING)
		app.logger.addHandler(file_handler)	
	
	return app
	
# Leave at the bottom of the file!
from app import models
from app.routes import *