"""
module __init__\n
Handles the routing for the PowerToken/Admin Flask application\n
Last modified by Abigail Franz on 2/21/2018
"""

import math
from flask import Flask, json, redirect, render_template, request, url_for
from ptadmin import PtAdmin
from ptmodels import PtLog, PtUser

# Creates a new Flask server application
app = Flask(__name__)

# The dashboard
@app.route("/")
@app.route("/home")
@app.route("/index")
@app.route("/default")
def home():
	admin = PtAdmin()
	return render_template("home.html", pt_users=admin.pt_users)
	
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