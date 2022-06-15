# minimal support for running functions locally

import logging
logger = logging.getLogger(__name__)

import os
import sys
import json
import importlib
import uuid
from datetime import datetime

from flask import request, make_response
from flask_restful import Resource, abort

from azure.storage.blob import StorageAccount
import azure.functions as func

class FlaskHttpRequest(object):
  def get_body(self):
    return request.get_data()
  
  def get_json(self):
    return request.get_json()

  @property
  def files(self):
    return request.files

  @property
  def form(self):
    raise NotImplementedError

  @property
  def headers(self):
    return request.headers

  @property
  def params(self):
    return request.args

  @property
  def url(self):
    return request.url

  @property
  def method(self):
    return request.method

class Manifest(object):
  def __init__(self, path):
    self.manifest = {}
    with open(path) as fp:
      self.manifest = json.load(fp)

  @property
  def bindings(self):
    try:
      return self.manifest["bindings"]
    except:
      return []

  def binding(self, **kwargs):
    for binding in self.bindings:
      for k, v in kwargs.items():
        if not k in binding or binding[k] != v:
          break
      else:
        return binding
    return None

  @property
  def http_trigger(self):
    return self.binding(type="httpTrigger", direction="in")

  @property
  def blob_out(self):
    return self.binding(type="blob", direction="out")

  @property
  def service_bus_trigger(self):
    return self.binding(type="serviceBusTrigger", direction="in")

class BlobBinding(object):
  def __init__(self, manifest):
    self.manifest = manifest
    path = self.manifest["path"]
    for k, v in os.environ.items():
      path = path.replace(f"%{k}%", v)
      path = path.replace(k, v)
    path = path.split("/")
    self.filename = path.pop()
    self.container = os.path.join(*path)

  def set(self, data):
    filename = self.filename.replace("{rand-guid}", str(uuid.uuid4()))
    StorageAccount.add(self.container, filename, data)

class ResourceWrapper(Resource):
  def __init__(self, function):
    self.function = function

  def get(self):
    if not "get" in self.function.manifest.http_trigger["methods"]: abort(404)
    return self.execute()

  def post(self):
    if not "post" in self.function.manifest.http_trigger["methods"]: abort(404)
    return self.execute()

  def execute(self):
    args = [ FlaskHttpRequest() ]
    if self.function.manifest.blob_out:
      args.append( BlobBinding(self.function.manifest.blob_out))
    result = self.function(*args)
    if isinstance(result, str):
      return make_response(result, 200)
    return make_response(result.get_body(), result.status_code)

class Function(object):
  def __init__(self, subdir, d, api):
    self.manifest = Manifest(os.path.join(subdir, d, "function.json"))
    pkg = ".".join([subdir.replace("/", "."), d])
    sys.path.append(subdir)
    mod = importlib.import_module(pkg)
    self.function = getattr(mod, "main")
    if self.manifest.http_trigger:
      logger.info(f"setting up API for {d} on {self.manifest.http_trigger['route']}")
      api.add_resource(
        ResourceWrapper,
        "/api/" + self.manifest.http_trigger["route"],
        endpoint=d,
        resource_class_args=(self,)
      )
    if self.manifest.service_bus_trigger:
      logger.info(f"setting up storage subscription for {d} on {self.manifest.service_bus_trigger['queueName']}")
      
      queueName = self.manifest.service_bus_trigger["queueName"]
      for k, v in os.environ.items():
        queueName = queueName.replace(f"%{k}%", v)
      
      StorageAccount.subscribe(queueName, self)

  def __call__(self, *args, **kwargs):
    return self.function(*args, **kwargs)

def create_app(path, api):
  for subdir, dirs, _ in os.walk(path):
    for d in dirs:
      try:
        Function(subdir, d, api)
      except FileNotFoundError:
        pass
