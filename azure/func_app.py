# minimal support for running functions locally

import logging
logger = logging.getLogger(__name__)

import os
import io
import sys
import json
import importlib
import uuid
from datetime import datetime
import inspect

import schedule

from flask import request, make_response, send_file, redirect
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
  def route_params(self):
    return request.view_args

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

  @property
  def timer_trigger(self):
    return self.binding(type="timerTrigger", direction="in")

class BlobBinding(object):
  def __init__(self, manifest):
    self.manifest = manifest
    path = self.manifest["path"]
    for k, v in os.environ.items():
      path = path.replace(f"%{k}%", v)
    for k, v in os.environ.items():    
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

  def get(self, *args, **kwargs):
    if not "get" in self.function.manifest.http_trigger["methods"]: abort(404)
    return self.execute()

  def post(self, *args, **kwargs):
    if not "post" in self.function.manifest.http_trigger["methods"]: abort(404)
    return self.execute()

  def delete(self, *args, **kwargs):
    if not "delete" in self.function.manifest.http_trigger["methods"]: abort(404)
    return self.execute()

  def execute(self):
    # assemble expected args
    args = [ FlaskHttpRequest() ]
    if "context" in self.function.parameters:
      context = func.Context()
      context.function_name = self.function.name
      args.append(context)
    if self.function.manifest.blob_out:
      args.append( BlobBinding(self.function.manifest.blob_out))

    # call function
    result = self.function(*args)

    # simple string output
    if isinstance(result, str):
      return make_response(result, 200)

    # HttpResponse
    if isinstance(result, func.HttpResponse):
  
      # check for redirect
      if result.status_code >= 300 and result.status_code < 400:
        return redirect(result.headers["Location"], result.status_code)
  
      data = result.get_body()
      headers = result.headers
      if isinstance(data, str):
        resp = make_response(data, result.status_code)
        if result.mimetype:
          resp.mimetype = result.mimetype
        return resp

      if result.mimetype:
        return send_file(io.BytesIO(data), mimetype=result.mimetype)
      else:
        return send_file(io.BytesIO(data), mimetype="application/octet-stream")

    logger.warn(f"⚠️ Unexpected function result: {result}")
    return make_response("ok", 200)

class Function(object):
  def __init__(self, subdir, d, api):
    try:
      self.manifest = Manifest(os.path.join(subdir, d, "function.local.json"))
    except:
      self.manifest = Manifest(os.path.join(subdir, d, "function.json"))
    pkg = ".".join([subdir.replace("/", "."), d])
    sys.path.append(subdir)
    mod = importlib.import_module(pkg)
    self.function = getattr(mod, "main")
    try:
      self.name = mod.__name__
    except:
      self.name = d

    if self.manifest.http_trigger:
      logger.info(f"  📍 Setting up API endpoint for {self.name} on {self.manifest.http_trigger['route']}")
      api.add_resource(
        ResourceWrapper,
        *self.route,
        endpoint=d,
        resource_class_args=(self,)
      )

    if self.manifest.service_bus_trigger:
      queueName = self.manifest.service_bus_trigger["queueName"]
      for k, v in os.environ.items():
        queueName = queueName.replace(f"%{k}%", v)
      logger.info(f"  ✋ subscribing {self.name} as handler for {queueName}")
      StorageAccount.subscribe(queueName, self)

    if self.manifest.timer_trigger:
      # basic support for limited set of cron schedules ;-)
      if self.manifest.timer_trigger["schedule"] == "0 */5 * * * *":
        logger.info(f"  ⏰ scheduling {self.name} every 5 minutes...")
        schedule.every(5).minutes.do(self, func.TimerRequest())
      elif self.manifest.timer_trigger["schedule"] == "*/5 * * * * *":
        logger.info(f"  ⏰ scheduling {self.name} every 5 seconds...")
        schedule.every(5).seconds.do(self, func.TimerRequest())
      else:
        logger.warn(f"unsupported schedule: {self.manifest.timer_trigger['schedule']}")

  @property
  def parameters(self):
    return inspect.signature(self.function).parameters

  @property
  def route(self):
    urls = []
    r = self.manifest.http_trigger["route"]
    if "{" in r:
      parts = r.split("/")
      url = []
      for part in parts:
        if part[0] == "{" and part[-1] == "}":
          if part[1:-1] == "*route":
            urls.append("/".join(url))
            url.append("<path:route>")
          else:
            if ":" in part:
              name, typing = part[1:-1].split(":")
              if typing[-1] == "?":
                urls.append("/".join(url))
              url.append(f"<{name}>")
            else:
              url.append(f"<{part[1:-1]}>")
        else:
          url.append(part)
      urls.append("/".join(url))
    else:
      urls.append(r) # no optional parts, simple route
    return [ "/api/" + url for url in urls ]

  def __str__(self):
    return self.name

  def __call__(self, *args, **kwargs):
    return self.function(*args, **kwargs)

def create_app(path, api):
  for subdir, dirs, _ in os.walk(path):
    for d in dirs:
      try:
        Function(subdir, d, api)
      except FileNotFoundError:
        pass
