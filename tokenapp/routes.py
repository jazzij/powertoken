# might need to look at this sometime: http://markjberger.com/flask-with-virtualenv-uwsgi-nginx/
from flask import Flask, render_template, request, json
import os, thread
import powertoken, weconnect

# Creates a new Flask server application
app = Flask(__name__)

# We will use the powertoken object to access the core PowerToken functions.
powertoken = powertoken.PowerToken()

# Stores the user's email (for referencing the tinydb) across the session
email = ""

# THE LANDING PAGE
@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html')

# WECONNECT FORM SUBMIT, FITBIT REDIRECT
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

# When Fitbit is all setup, login.html redirects to here
@app.route('/result', methods=['GET', 'POST'])
def result():
	data = request.data
	convData = data.decode('utf8')
	datajs = json.loads(convData)

	# Stores access token in a JSON file
	#jsonStr = '{"userToken":"' + datajs["tok"] + '"}'
	#with open("data/fb.json", "w+") as file:
	#	file.write(jsonStr)

	powertoken.completeFbLogin(email, datajs["tok"])
	
	return render_template('home.html', fb_response="Login successful")

@app.route('/start', methods=['GET', 'POST'])
def start():
	thisEmail = ""
	if request.method == 'GET':
		thisEmail = email
	elif request.method == 'POST':
		thisEmail = request.form["email"]
	thread.start_new_thread(render_template, ('running.html'))
	thread.start_new_thread(powertoken.startExperiment, (thisEmail))

@app.route('/test', methods=['GET', 'POST'])
def test():
	powertoken.runTests()
	#data = request.data
	return render_template('home.html')

if __name__ == "__main__":
	app.run(debug=False)
