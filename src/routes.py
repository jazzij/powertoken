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
		return redirect(url_for("fb_login"))

@app.route("/fb_login", methods=["GET"])
def fb_login():
	return render_template("fb_login.html")

@app.route("/fb_response", methods=["POST"])
def fb_response():
	return render_template("home.html")

# In production, debug will probably be set to False.
if __name__ == "__main__":
	app.run(debug=True)