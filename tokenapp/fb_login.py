from flask import Flask, render_template, request


app = Flask(__name__)

@app.route('/callback')
def oath_callback():
	session_code = request.


if __name__ == "__main__":
        app.run(debug=True)
