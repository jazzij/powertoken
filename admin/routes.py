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