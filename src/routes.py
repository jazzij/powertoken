from flask import Flask, json, redirect, render_template, request, url_for
import requests
import powertoken

# Creates a new Flask server application
app = Flask(__name__)

# We will use the powertoken object to access the core PowerToken functions.
powertoken = powertoken.PowerToken()

# Stores the username (for referencing the tinydb) across the session
username = ""

# The landing page
@app.route("/")
@app.route("/home")
def home():
	welcome = ""
	if username:
		welcome = "Welcome, %s!" % (username,)
	return render_template("home.html", welcome=welcome)

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
		username = request.form["username"]
		if not powertoken.isUsernameUnique(username):
			errorMessage = "Sorry. Someone else has already chosen that username."
			return render_template("pt_login.html", error_not_unique=errorMessage)
		else:
			# Adds a new user to the TinyDB and redirects to /wc_login
			powertoken.createUser(username)
			return redirect(url_for("wc_login"))

@app.route("/wc_login", methods=["GET", "POST"])
def wc_login():
	# User is redirected here after choosing a PowerToken username
	if request.method == "GET":
		return render_template("wc_login.html")

	# wc_login.html form submit uses POST
	elif request.method == "POST":
		# Logs user into WEconnect
		email = request.form["email"]
		password = request.form["password"]
		loginSuccessful = powertoken.loginToWc(username, email, password)
		if not loginSuccessful:
			errorMessage = "Login failed. Try again."
			return render_template("wc_login.html", login_error=errorMessage)

		# Redirects to Fitbit login page
		return redirect(url_for("fb_login"))

@app.route("/fb_login", methods=["GET", "POST"])
def fb_login():
	# The user is redirected here after a successful WEconnect login.
	if request.method == "GET":
		return render_template("fb_login.html")

	# When Fitbit is all setup, fb_login.js redirects here.
	elif request.method == "POST":
		print("Called the POST section of fb_login()")
		# Converts the response into the correct format and passes it to a function
		# that stores the user's access token in the TinyDB
		data = request.data
		convData = data.decode('utf8')
		datajs = json.loads(convData)
		powertoken.completeFbLogin(username, datajs["tok"])

		# This line is insignificant but must be here
		return render_template("home.html")

# In production, debug will probably be set to False.
if __name__ == "__main__":
	app.run(debug=True)