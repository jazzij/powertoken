"""
Database debug module\n
Created by Jasmine Jones on 12/4/2018.\n
Last Modified by Jasmine Jones on 12/4/2018.
"""

import db
import json
from flask import jsonify

#in db.py : Base.metadata.bind = engine
meta = db.Base.metadata
result = {}
for table in meta.sorted_tables:
	result[table.name] = [dict(row) for row in db.engine.execute(table.select())]

print (result)

'''
FORMAT OF TABLE JSON
- just json: https://stackoverflow.com/questions/883977/display-json-as-html
- to html table: https://github.com/spoqa/dodotable
- https://www.tutorialspoint.com/flask/flask_sqlalchemy.htm
'''

def delete_all_content():
	try:
		for tables in db.Base.metadata.sorted_tables:
			db.session.query(table).delete()
		db.session.commit()
	except:
		db.session.rollback()