"""
setup.py
This file exists to enable the Flask-based application to be installed.
It should be at the same level as powertoken/ application folder
To install, run >> pip install -e .
Then >> flask run
"""
from setuptools import setup

setup(
	name='powertoken',
	packages=['powertoken'],
	include_packages_data=True,
	install_requires=['flask', 'flask-sqlalchemy', 'sqlalchemy',],
)
