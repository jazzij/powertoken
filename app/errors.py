"""
Handles errors encountered by the PowerToken Flask app.\n
Created by Abigail Franz on 3/12/2018\n
Last modified by Abigail Franz on 3/13/2018
"""

from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
	return redirect("https://http.cat/404"), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return redirect("https://http.cat/500"), 500