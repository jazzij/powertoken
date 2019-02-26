"""
Simple script to initially create database when \n
all tables are setup (in models) and initialized (in __init__.py) 
Created by Jasmine J 12/19/2019.
"""
import os.path
from powertoken.models import db

#create DB if not already there
def create_database(db):
	if not os.path.isfile(app.config["SQLALCHEMY_DATABASE_URI"]):
		print("Creating new database at: {}".format(app.config["SQLALCHEMY_DATABASE_URI"]))
	db.create_all()

def weconnectCode():
	print("we doth connect")
	return 1