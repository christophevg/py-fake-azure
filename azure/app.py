import logging
logger = logging.getLogger(__name__)

import os

# load the environment variables for this setup
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "DEBUG"

# setup logging infrastructure

logging.getLogger("urllib3").setLevel(logging.WARN)

FORMAT  = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S %z"

logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)
formatter = logging.Formatter(FORMAT, DATEFMT)
logging.getLogger().handlers[0].setFormatter(formatter)

# setup Flask server and API

from flask import Flask, request
from flask_cors import CORS, cross_origin

import flask_restful

import json
from datetime import datetime

import fire

from azure import func_app, app_svc

import azure.functions as func

class Encoder(json.JSONEncoder):
  def default(self, o):
    if isinstance(o, datetime):
      return o.isoformat()
    if isinstance(o, set):
      return list(o)
    if isinstance(o, func.HttpResponse):
      return o.body
    return super().default(o)

func_app_path = os.environ.get("FUNC_APP")
app_svc_path  = os.environ.get("APP_SVC")

logger.info(f"running from {func_app_path} + {app_svc_path}")

server   = None
socketio = None
api      = None

if app_svc_path:
  server, socketio = app_svc.create_app(app_svc_path)

if not server:
  logger.info("setting up API server")
  server = Flask(__name__)

if func_app_path:
  cors = CORS(server, resources={r"*": {"origins": "*"}})
  api = flask_restful.Api(server)
  server.config['RESTFUL_JSON'] =  {
    "indent" : 2,
    "cls"    : Encoder
  }
  func_app.create_app(func_app_path, api=api)

import azure.oauth
