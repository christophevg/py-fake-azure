import logging
logger = logging.getLogger(__name__)

from flask import Flask
from flask_cors import CORS
import flask_restful

import json
from datetime import datetime

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

class MockedAzure(object):
  def __init__(self):
    self.func_app = None
    self.app_svc  = None
    self.server   = None
    self.socketio = None
    self.api      = None

  def __str__(self):
    return ""

  def serve_func_app(self, path):
    self.func_app = path
    return self

  def serve_app_svc(self, path):
    self.app_svc = path
    return self
  
  def setup(self):
    if self.app_svc:
      self.server, self.socketio = app_svc.create_app(self.app_svc)

    if not self.server:
      logger.debug("🌎 Setting up server for function app.")
      self.server = Flask(__name__)

    if self.func_app:
      CORS(self.server, resources={r"*": {"origins": "*"}})
      self.api = flask_restful.Api(self.server)
      self.server.config['RESTFUL_JSON'] =  {
        "indent" : 2,
        "cls"    : Encoder
      }
      func_app.create_app(self.func_app, api=self.api)

  def run(self):
    self.setup()
    if self.socketio:
      self.socketio.run(server, debug=True)
    else:
      self.server.run()
