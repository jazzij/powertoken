PowerToken Flask App (Last Update, 11/8/2017)

Dependencies:
Flask, http://flask.pocoo.org/
Python 2.7, (but should be compatible with Python 3)
Javascript / Fetch API, https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
Fitbit Web API, https://dev.fitbit.com/reference/web-api/quickstart/

Interaction:
Users enter the login details into the form, and in the Fitbit website. They get redirected to the landing page, and that's it for them.
On the server side, some magic and ladders to get all the data into a form where it can be saved to a json file for easy access later.


Tips:
Best to setup a virtualenv to setup Flask, see documentation for details

Using Fitbit API requires additional setup- if you don't have an account 
and app setup, see Web API quickstart. This app using implicit auth flow (implemented with javascript / html), saves the access token to a json file on the server, and completes all subsequent necessary API calls in python


The Flow: 
Run 'python routes.py' to start the flask server. The server will serve all webpages as part of the app. Check your server output to see what port its running on
(usually something like localhost:5000)

In routes.py you will see a collection of methods that are mapped to URLS (routes). 
You shouldn't try to manually enter these URLS because some require HTTP data. 

In the /templates folder, you will see a collection of HTML files. These are served and modified by the python code
They are very minimal. The key files are home.html (the landing page) and login.html (runs the javascript to connect to fitbit server)
Similar to the routes, manually entering a html template might not yield the behavior to expect, because some of the templates are not hard-coded HTML, but populated by the python code as it is served.

In the /static folder, you will find the golden egg. The javascript file (which is run from login.html) to login to fitbit, go through the OATH process and send the code back to the server via the /results route
There is probably a more finessed way of doing this, but hey, it works.

The user information entered by the user is not saved, only the access token received from the APIs and their userID



