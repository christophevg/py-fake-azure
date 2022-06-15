import logging
logger = logging.getLogger(__name__)

import os

# load the environment variables for this setup
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "INFO"

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

from azure.map import generate

class Encoder(json.JSONEncoder):
  def default(self, o):
    if isinstance(o, datetime):
      return o.isoformat()
    if isinstance(o, set):
      return list(o)
    if isinstance(o, func.HttpResponse):
      return o.body
    return super().default(o)

class MockedAzure(object):
  def __init__(self):
    self.func_app = None
    self.app_svc  = None

  def __str__(self):
    return ""

  def serve_func_app(self, path):
    self.func_app = path
    return self

  def serve_app_svc(self, path):
    self.app_svc = path
    return self
  
  def run(self):
    server   = None
    socketio = None
    if self.app_svc:
      server, socketio = app_svc.create_app(self.app_svc)

    if not server:
      logger.info("setting up API server")
      server = Flask(__name__)

    if self.func_app:
      cors = CORS(server, resources={r"*": {"origins": "*"}})
      api = flask_restful.Api(server)
      server.config['RESTFUL_JSON'] =  {
        "indent" : 2,
        "cls"    : Encoder
      }
      func_app.create_app(self.func_app, api=api)

    if socketio:
      socketio.run(server, debug=True)
    else:
      server.run()

class Mapper(object):
  def __init__(self):
    pass

  def map(self, path, outfile, format="png"):
    generate(path, outfile, format)

if __name__ == '__main__':
  fire.Fire(MockedAzure)
