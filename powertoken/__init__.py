"""
__init__.py
Setup for Powertoken Flask application
To install, go up to level of enclosing directory, and run >>pip install -e .
(See ../setup.py for details)
"""
import os.path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config	#powertoken defined configuration class

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(config_class)
	db.init_app(app)
	migrate.init_app(app, db)
	return app

app = create_app()

from powertoken.models import User, Activity, Event, Log, Day, Admin, Error
import powertoken.routes
