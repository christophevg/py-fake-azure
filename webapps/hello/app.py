from flask import Flask, send_from_directory
app = Flask(__name__, static_url_path="")

@app.route("/")
def hello():
  return "Hello, World!\n"

@app.route("/form")
def form():
  return send_from_directory("", "form.html")

@app.route("/js/jquery.min.js")
def js():
  return send_from_directory("", "jquery.min.js")
