from flask import Flask
from flask import render_template
123

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("index.html")
