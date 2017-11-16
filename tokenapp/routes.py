# might need to look at this sometime: http://markjberger.com/flask-with-virtualenv-uwsgi-nginx/
from flask import Flask, render_template, request, json
import powertoken_setup
import weconnect_fitbit

app = Flask(__name__)

#THE LANDING PAGE
@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html')

#WECONNECT FORM SUBMIT, FITBIT REDIRECT
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		received = request.form

		# If user is already logged in, tells him/her so
		if powertoken_setup.isLoggedIn():
			return render_template('home.html', wc_response="You are already logged into WEconnect.")

		#INSERT LOGIN CODE HERE, & ADD received["token"] to dict
		#with open('userID.json', 'w') as f:
		#	json.dump(received, f, ensure_ascii=False)
		#print (request)
		#print (request.form["name"])
		#print (request.form["psk"])

		# Logs user into WEconnect if he/she isn't already
		powertoken_setup.loginToWc(request.form["name"], request.form["psk"])

		return render_template('home.html', wc_response="Login successful")

	elif request.method == 'GET':
		return render_template('login.html')

#THE CALLBACK for FITBIT API (http://host-url/fb_login). 
#Note: login.html contains javascript
@app.route('/fb_login', methods=['GET'])
def fb_login():
	return render_template('login.html')

#WHEN FITBIT is all setup, login.html sends 
@app.route('/result', methods=['GET', 'POST'])
def result():
	data = request.data
	print(data)
	convData = data.decode('utf8')
	datajs = json.loads(convData)
	print(datajs)
	print(datajs["tok"])

	# Stores access token in a JSON file
	with open("fb.json", "w+") as file:
		file.write(data)

	print('Result achieved')
	
	return render_template('home.html', fb_response="Login successful")

@app.route('/start', methods=['GET', 'POST'])
def start():
	powerToken = weconnect_fitbit.PowerToken()
	powerToken.listenForWcChange()

@app.route('/test', methods=['GET', 'POST'])
def test():
	print('Post to test')
	data = request.data
	print(data)
	return render_template('home.html')

if __name__ == "__main__":
        app.run(debug=True)
