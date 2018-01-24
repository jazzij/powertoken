from flask import Flask, json, redirect, render_template, request, url_for
import requests, shelve
import powertoken

# Creates a new Flask server application
app = Flask(__name__)

# We will use the powertoken object to access the core PowerToken functions.
powertoken = powertoken.PowerToken()

# Stores the username (for referencing the TinyDB) across the session
session = { "username": "" }

# The landing page
@app.route("/")
@app.route("/home")
def home():
	print("home: username = %s" % (session["username"],))
	welcome = ""
	start_code = ""
	if session["username"]:
		welcome = "Welcome, %s!" % (session["username"],)
		start_code = "<a href={{url_for('start')}} class='btn'>START</a>"
	return render_template("home.html", welcome=welcome, start_code=start_code)

# Clears all logins! Don't do this unless you really know what you're doing.
# We will probably remove this option altogether in a production environment.
@app.route('/reset')
def reset():
	powertoken.resetLogins()
	return render_template("home.html")

@app.route("/pt_login", methods=["GET", "POST"])
def pt_login():
	if request.method == "GET":
		return render_template("pt_login.html")
	elif request.method == "POST":
		session["username"] = request.form["username"]
		print("pt_login [POST]: username = %s" % (session["username"],))

		# Checks if the user already exists in the TinyDB
		if powertoken.isCurrentUser(session["username"]):

			# If the user is already logged into WEconnect and Python, he/she is
			# redirected to the home page
			if (powertoken.isLoggedIntoWc(session["username"]) and 
				powertoken.isLoggedIntoFb(session["username"])):
				return redirect(url_for("home"))

			# Otherwise, the user is sent right to the WEconnect login
			else:
				return redirect(url_for("wc_login"))

		# If this is a new user, adds him/her to the TinyDB and redirects to the
		# WEconnect login
		else:
			powertoken.createUser(session["username"])
			return redirect(url_for("wc_login"))

@app.route("/wc_login", methods=["GET", "POST"])
def wc_login():
	# User is redirected here after choosing a PowerToken username
	if request.method == "GET":
		print("wc_login [GET]: username = %s" % (session["username"],))
		return render_template("wc_login.html")

	# wc_login.html form submit uses POST
	elif request.method == "POST":
		print("wc_login [POST]: username = %s" % (session["username"],))
		# Logs user into WEconnect
		email = request.form["email"]
		password = request.form["password"]
		loginSuccessful = powertoken.loginToWc(session["username"], email, password)
		if not loginSuccessful:
			errorMessage = "Login failed. Try again."
			return render_template("wc_login.html", login_error=errorMessage)

		# Redirects to Fitbit login page
		return redirect(url_for("fb_login"))

@app.route("/fb_login", methods=["GET", "POST"])
def fb_login():
	# The user is redirected here after a successful WEconnect login.
	if request.method == "GET":
		print("fb_login [GET]: username = %s" % (session["username"],))
		return render_template("fb_login.html")

	# When Fitbit is all setup, fb_login.js redirects here.
	elif request.method == "POST":
		print("fb_login [POST]: username = %s" % (session["username"],))
		# Converts the response into the correct format and passes it to a function
		# that stores the user's access token in the TinyDB
		data = request.data
		convData = data.decode('utf8')
		datajs = json.loads(convData)
		powertoken.completeFbLogin(session["username"], datajs["tok"])

		# This code will never be called but must be here
		return render_template("home.html")

@app.route("/start", methods=["GET"])
def start():
	powertoken.startExperiment(session["username"])

	# This code will never be called
	return render_template("home.html")

# In production, debug will probably be set to False.
if __name__ == "__main__":
	app.run(debug=True)