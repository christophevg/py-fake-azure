import logging
logger = logging.getLogger(__name__)

import os
import sys
import xmltodict
import json
from collections import OrderedDict
from graphviz import Digraph
from pathlib import Path

from azure.func_app import Manifest

class DotDiagram(object):
  def __init__(self):
    self.diagram = None
    self.nodes   = []
    self.edges   = []

  def reset(self):
    self.nodes = []
    self.edges = []

  def generate(self, path, format="svg", direction="TB", engine="dot"):
    self.diagram = Digraph(
      self.__class__.__name__,
      filename = path,
      format   = format,
      engine   = engine
    )
    self.diagram.attr(rankdir=direction)
    self.reset()

    self.render()
    
    self.diagram.attr(overlap="scalexy", **self.diagram_args())
    self.diagram.render()
    logger.debug("generated {}".format(str(path) + "." + format))

    return str(path) + "." + format

  def diagram_args(self):
    return {}

  def render(self):
    raise NotImplementedError

  def _node(self, name, label="", diagram=None, **kwargs):
    if diagram is None: diagram = self.diagram
    kwargs["id"] = name
    if "URL" in kwargs: kwargs["target"] = "_top"
    if not name in self.nodes:
      diagram.node(name, label, **kwargs)
      self.nodes.append(name)

  def _edge(self, origin, destination, diagram=None, **kwargs):
    if diagram is None: diagram = self.diagram
    id = origin + "-" + destination
    if "URL" in kwargs: kwargs["target"] = "_top"
    kwargs["id"] = id
    if not id in self.edges:
      diagram.edge(origin, destination, **kwargs)
      self.edges.append(id)

class FunctionAppMap(DotDiagram):
  def __init__(self, functions, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.functions = functions

  def diagram_args(self):
    return {};

  def render(self):
    for name, config in self.functions.items():
      if config["type"] != "api" or len(config["out"]) > 0:
        color = {
          "api"      : "lightgreen",
          "queue"    : "lightcoral",
          "storage"  : "lightpink",
          "function" : "lightblue"
        }[config["type"]]
        self._node(name, name, style="filled", fillcolor=color)
        for out in config["out"]:
          self._edge(name, out)

def generate(path, outfile, format):
  functions = {}

  with open("storage-queues.json") as fp:
    storage_queues = json.load(fp)
    for st, queue in storage_queues.items():
      functions[st]    = { "type" : "storage", "out" : [ queue ] }
      functions[queue] = { "type" : "queue",   "out" : [] }

  for subdir, dirs, _ in os.walk(path):
    for d in dirs:
      try:
        manifest = Manifest(os.path.join(subdir, d, "function.json"))
        if manifest.http_trigger:
          name = manifest.http_trigger["route"]
          functions[name] = { "type" : "api", "in" : "http", "out" : [] }
        elif manifest.service_bus_trigger:
          name = d
          functions[name] = { "type" : "function", "in" : "queue", "out" : [] }          
          queue = manifest.service_bus_trigger["queueName"]
          functions[queue]["out"].append( d )
        else:
          print(json.dumps({
            "http_trigger"        : manifest.http_trigger,
            "blob_out"            : manifest.blob_out,
            "service_bus_trigger" : manifest.service_bus_trigger
          }, indent=2))
          assert False

        if manifest.blob_out:
          functions[name]["out"].append(manifest.blob_out["path"].split("/")[0])

      except FileNotFoundError:
        pass

  # print(json.dumps(functions, indent=2))
  FunctionAppMap(functions).generate(outfile, format)