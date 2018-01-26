from flask import Flask, render_template, url_for
import pressthread

app = Flask(__name__)

@app.route("/")
@app.route("/home")
@app.route("/index")
@app.route("/default")
def home():
    return render_template("pressme.html")

@app.route("/press")
def press():
    pt = pressthread.PressThead(2, "User-1")
    pt.start()
    return render_template("pressme.html")

if __name__ == "__main__":
    app.run(debug=True, threaded=True)