"""
WSGI entry point for Gunicorn. Can be run with the command:
`gunicorn --bind <host>:<port> wsgi [options]`
"""

from powertoken import app as application

if __name__ == "__main__":
	application.run()
