# Welcome to the PowerToken Project

This project is part of the "Wearables for Recovery" project conducted by researchers at the University of Minnesota.


## Brief Intro

This project uses the Fitbit Web API and the WEconnect API (in alpha) to transform data collected on social interactions into a wearable progress display. This project enables us to study new forms of technology for supporting and enhancing people's recovery experience.


## Who We Are

Researchers are affiliated with the GroupLens Center for Social and Human-Centered Computing. 


For more info, check out our website at [GroupLens](https://grouplens.org).

The code for this project is licensed under the MIT License.

## How to Setup
1. Start your virtual environment, make sure all requirements are met (pip install -r requirements.txt)
2. Set up and SOURCE your export variables (export the variables below with your own app/system details)
3. _o_ Create your database 

FOLDER STRUCTURE
/powertoken
	data/ --> pt_data.db
	background/
	setup.py 
	requirements.txt
	config.py 
    	powertoken/ (app)
            __init__.py
	    routes.py
	    models.py
	    ...
        static/
            style.css
        templates/
            layout.html
            index.html
            login.html
            ... 
            
## What you need
The requirements.txt file lists all the dependencies and packages for running this code
You also need to set your environment by EXPORTing the following variables.

FLASK_APP
SECRET_KEY 
DATABASE_URL
MAIL_SERVER
MAIL_PORT
MAIL_USE_TLS
MAIL_USERNAME
MAIL_PASSWORD
PT_ADMINS (admin email addresses you'd like to get)
LOG_PATH
DB_PATH (from the directory that contains powertoken, $PWD/powertoken/data/pt_data.db)

HOW TO CREATE DB
from python interpreter (same level as powertoken/):
>> from background.database import init_db
>> init_db()
OR via FLASK
go to localhost:xxxx/createDB

MIGRATION
Setup SQLALCHEMY Alembic (nice tutorial here:https://www.learndatasci.com/tutorials/using-databases-python-postgres-sqlalchemy-and-alembic/)
After initializing, (>> alembic stamp head)
To run migration, make changes to data.models and run
>> alembic revision --autogenerate -m "describe here" 
>>alembic upgrade head 



