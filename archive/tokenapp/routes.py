# routes.py
# Python Flask main application. Handles form processing and routing.
# To run this application, type "python routes.py" at the command line.
# Created by: Jasmine Jones
# Last modified by: Abigail Franz on 1/20/2018

# Might need to look at this sometime: http://markjberger.com/flask-with-virtualenv-uwsgi-nginx/
from flask import Flask, render_template, request, json
import os
import powertoken

# Creates a new Flask server application
app = Flask(__name__)

# We will use the powertoken object to access the core PowerToken functions.
powertoken = powertoken.PowerToken()

# Stores the user's email (for referencing the tinydb) across the session
email = ""

# The landing page
@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html')

# Clears all logins! Don't do this unless you really know what you're doing.
# We will probably remove this option altogether in a production environment.
@app.route('/reset')
def reset():
	powertoken.resetLogins()
	return render_template('home.html')

# WEconnect form submit, Fitbit redirect
@app.route('/login', methods=['GET', 'POST'])
def login():
	# WEconnect form submit uses POST
	if request.method == 'POST':
		received = request.form

		# If user is already logged in, tells him/her so
		if powertoken.isLoggedIntoWc(request.form["name"]):
			return render_template('home.html', wc_response="You are already logged into WEconnect.")

		# Logs user into WEconnect if he/she isn't already
		powertoken.loginToWc(request.form["name"], request.form["psk"])
		email = request.form["name"]

		return render_template('home.html', wc_response="Login successful")

	# Fitbit redirect uses GET
	elif request.method == 'GET':
		return render_template('login.html')

# The callback for Fitbit API (http://host-url/fb_login). 
# Note: login.html contains JavaScript
@app.route('/fb_login', methods=['GET'])
def fb_login():
	# First, sees if the user is already logged into Fitbit
	if powertoken.isLoggedIntoFb(email):
		return render_template('home.html', fb_response="You are already logged into Fitbit.")

	# If not, logs in and stores access token
	else:
		return render_template('login.html')

# When Fitbit is all set up, login.html redirects to here
@app.route('/result', methods=['GET', 'POST'])
def result():
	# Converts the response into the correct format and passes it to a function
	# that stores the user's access token in the TinyDB
	data = request.data
	convData = data.decode('utf8')
	datajs = json.loads(convData)
	powertoken.completeFbLogin(email, datajs["tok"])
	
	return render_template('home.html', fb_response="Login successful")

@app.route('/start', methods=['GET', 'POST'])
def start():
	thisEmail = ""

	# If the user just logged in for the first time
	if request.method == 'GET':
		thisEmail = email

	# If this is a returning user
	elif request.method == 'POST':
		thisEmail = request.form["email"]

	powertoken.startExperiment(thisEmail)

# Runs unit tests. For testing only, not production.
@app.route('/test', methods=['GET', 'POST'])
def test():
	powertoken.runTests()
	return render_template('home.html')

# In production, debug will probably be set to False.
if __name__ == "__main__":
	app.run(debug=True)
