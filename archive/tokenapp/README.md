PowerToken Flask App (Last Update, 1/20/2018)


Dependencies:

Flask (documentation at http://flask.pocoo.org/)
Python 2.7 (but should be compatible with Python 3)
JavaScript Fetch API (https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
Fitbit Web API (https://dev.fitbit.com/reference/web-api/quickstart/)
WEconnect Web API (documentation not publicly available)


Interaction:

If the user has never logged into PowerToken before, he/she must enter his/her WEconnect login details into the form on the landing page. Then the user is redirected to the Fitbit login page, where he/she must grant the application permission to access his/her data. The user is sent back to the landing page and must click the START button at the bottom. That's pretty much it.

As a side note, there is currently an option for the user to enter his/her WEconnect username on the first page if he/she has already logged into PowerToken. As the server will be running continuously, this option will probably never be used in production. It is mainly there for testing.

On the server side, some magic occurs to get all the data into a JSON-based database for easy access later. Users are currently identified by their WEconnect usernames, but we will probably assign each a unique ID later.


Tips:

It's best to setup a virtualenv to setup Flask; see the Flask documentation for details.

Using the Fitbit API requires additional setup--if you don't have an account and app set up, see the Web API quickstart. This app uses implicit OATH flow (implemented with JavaScript / HTML), saves the access token to a JSON-based database on the server, and completes all subsequent API calls in Python.


The Flow: 

Run 'python routes.py' to start the Flask server. The server will serve all webpages as part of the app. Check your server output to see what port it's running on (usually something like localhost:5000). We have ours set to run on an Apache/2.4.18 (Ubuntu) Server at powertoken.grouplens.org:443.

In routes.py you will see a collection of methods that are mapped to URLs (routes). You shouldn't try to manually enter these URLs because some require HTTP data. 

In the /templates folder, you will see a collection of HTML files. These are served and modified by the Python code. They are very minimal. The key files are home.html (the landing page) and login.html (runs the javascript to connect to fitbit server).

Similar to the routes, manually entering an HTML template might not yield the behavior you expect, because some of the templates are not hard-coded HTML, but populated by the Python code as they are served.

In the /static folder, you will find the golden egg. The JavaScript file (which is run from login.html) logs the user into Fitbit, goes through the OATH process, and sends an access code back to the server via the /results route.
There is probably a more finessed way of doing this, but hey, it works.

The information entered by the user is not saved, only the access token received from the APIs and their userID.



