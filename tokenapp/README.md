PowerToken Flask App (Last Update, 11/8/2017)

Dependencies:
Flask, http://flask.pocoo.org/
Python 2.7, (but should be compatible with Python 3)
Javascript / Fetch API, https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
Fitbit Web API, https://dev.fitbit.com/reference/web-api/quickstart/

Best to setup a virtualenv to setup Flask, see documentation for details

Using Fitbit API requires additional setup- if you don't have an account 
and app setup, see Web API quickstart. This app using implicit auth flow (implemented with javascript / html), saves the access token to a json file on the server, and completes all subsequent necessary API calls in python


