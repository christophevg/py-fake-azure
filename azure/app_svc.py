import logging
logger = logging.getLogger(__name__)

import sys
import importlib

def create_app(path):
  server = None
  socketio = None
  
  p = path.replace("/", ".") + ".app"
  sys.path.append(path)
  mod = importlib.import_module(p)
  try:
    server = getattr(mod, "app")
  except:
    server = getattr(mod, "server")
  try:
    socketio = getattr(mod, "socketio")
  except:
    pass
    
  logger.info(f"loaded webapp {p}")
  return server, socketio
