from flask import Flask, request, redirect
from flask.sessions import SecureCookieSession

app = Flask(__name__)
session = SecureCookieSession()
session.permanent = True
session.modified = True
print("Created app and session objects.")

client_id = "22CV5V"
callback_url = "https://powertoken.grouplens.org/fitbit_result"
auth_url = "https://www.fitbit.com/oath2/authorize"
redirect_url = "{}?response_type=code&client_id={}&redirect_uri={}&scope=activity".format(
	auth_url, client_id, callback_url)

@app.route("/")
@app.route("/index")
def index():
	return redirect(url_for("fitbit_login"))

@app.route("/fitbit_login", methods=["GET", "POST"])
def fitbit_login():
	if request.method == "GET":
		session["username"] = "Jill Pole"
		session.modified = True
		return redirect(redirect_url)

@app.route("/fitbit_result")
def fitbit_result():
	fb_token = request.args.get("access_token")
	print(fb_token)
	return redirect(url_for("index"))

if __name__ == "__main__":
	app.run(debug=True)