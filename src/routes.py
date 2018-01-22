from flask import Flask, json, redirect, render_template, request, url_for

# Creates a new Flask server application
app = Flask(__name__)

# The landing page
@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html")

@app.route("/pt_login", methods=["GET", "POST"])
def pt_login():
	if request.method == "GET":
		return render_template("pt_login.html")
	elif request.method == "POST":
		# Process PT info and redirect to /wc_login
		return redirect(url_for("wc_login"))

@app.route("/wc_login", methods=["GET", "POST"])
def wc_login():
	if request.method == "GET":
		return render_template("wc_login.html")
	elif request.method == "POST":
		# Process WC info and redirect to /fb_login
		data = {
			"email": request.form["email"],
			"password": request.form["password"]
		}
		result = requests.post("https://palalinq.herokuapp.com/api/People/login", data=data)
		if result.status_code != 200:
			print("Login error")
			exit()
		jres = result.json()
		userId = str(jres["accessToken"]["userId"])
		userToken = str(jres["accessToken"]["id"])
		print("Received ID and token from WEconnect: %s, %s" % (userId, userToken))
		return redirect(url_for("fb_login"))

@app.route("/fb_login", methods=["GET", "POST"])
def fb_login():
	if request.method == "GET":
		return render_template("fb_login.html")
	elif request.method == "POST":
		dataRaw = request.data.decode("utf-8")
		dataJson = json.loads(dataRaw)
		print("The token received from Fitbit: %s" % (datajs["tok"],))
		return redirect(url_for("home"))

# When Fitbit is all set up, fb_login.js redirects to here
@app.route("/fb_response", methods=["GET", "POST"])
def fb_response():
	# Converts the response into the correct format and passes it to a function
	# that stores the user's access token in the TinyDB
	data = request.data
	convData = data.decode("utf8")
	datajs = json.loads(convData)
	#powertoken.completeFbLogin(email, datajs["tok"])
	print("The token received from Fitbit: %s" % (datajs["tok"],))
	
	return render_template("home.html")

# In production, debug will probably be set to False.
if __name__ == "__main__":
	app.run(debug=True)