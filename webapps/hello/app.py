import logging
logger = logging.getLogger(__name__)

from flask import Flask, send_from_directory
app = Flask(__name__, static_url_path="")

@app.route("/")
def hello():
  logger.debug(f"🍺 Pouring a greeting.")
  return "Hello, World!\n"

@app.route("/form")
def form():
  logger.debug(f"🍺 Pouring form.html.")
  return send_from_directory("", "form.html")

@app.route("/js/jquery.min.js")
def js():
  logger.debug(f"🍺 Pouring jquery.min.js.")
  return send_from_directory("", "jquery.min.js")
