"""
Initializes the PowerToken Flask app variables.\n
Created by Abigail Franz on 3/12/2018.\n
Last modified by Abigail Franz on 3/13/2018.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "admin_login"

# TODO: Set up mail server so that administrators get an email in the event of
# a system failure. (This code currently does nothing).
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

# Leave at the bottom of the file!
from app import routes, errors, models