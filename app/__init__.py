"""
PowerToken Flask app initialization module.\n
Created by Abigail Franz on 3/12/2018\n
Last modified by Abigail Franz on 3/13/2018
"""

from flask import Flask, current_app
from flask.sessions import SecureCookieSession
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import logging
from logging.handlers import SMTPHandler

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "admin_login"
session = SecureCookieSession()
session.permanent = True
session.modified = True
with app.app_context():
	print(current_app.name)
print("Created app and session objects.")

if not app.debug:
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

from app import routes, errors, models