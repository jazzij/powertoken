"""
Handles errors encountered by the PowerToken Flask app.\n
Created by Abigail Franz on 3/12/2018.\n
Last modified by Abigail Franz on 3/26/2018.
"""

from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
	return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template("500.html"), 500