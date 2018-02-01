# admin.py

from flask import Flask, json, redirect, render_template, request, url_for

# Creates a new Flask server application
app = Flask(__name__)

# The dashboard
@app.route("/")
@app.route("/home")
@app.route("/index")
@app.route("/default")
def home():
	return render_template("home.html")
	
@app.route("/manage")
def manage():
	return render_template("manage.html")
	
@app.route("/stats")
def stats():
	return render_template("stats.html")
	
@app.route("/docs")
def docs():
	return render_template("docs.html")
	
if __name__ == "__main__":
	app.run(debug=True)