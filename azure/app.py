import logging
logger = logging.getLogger(__name__)

import os

# load the environment variables for this setup
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "DEBUG"

# setup logging infrastructure

logging.getLogger("urllib3").setLevel(logging.WARN)
logging.getLogger("graphviz").setLevel(logging.WARN)

FORMAT  = os.environ.get("LOGGER_FORMAT", "%(message)s")
DATEFMT = "%Y-%m-%d %H:%M:%S %z"

LOG_FILE = os.environ.get("LOG_FILE")
if LOG_FILE:
  logging.basicConfig(
    level=LOG_LEVEL,
    filename=LOG_FILE, filemode="a",
    format=FORMAT, datefmt=DATEFMT
  )
else:
  logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)

formatter = logging.Formatter(FORMAT, DATEFMT)
logging.getLogger().handlers[0].setFormatter(formatter)

common_path    = os.environ.get("COMMON_MODULES_PATH", None)
func_app_paths = os.environ.get("FUNC_APP", "").split(" ")
app_svc_path   = os.environ.get("APP_SVC",  None)

from azure.mock import MockedAzure

mocked_azure = MockedAzure()
if common_path:
  mocked_azure.with_common(common_path)

for path in func_app_paths:
  mocked_azure.serve_func_app(path)

mocked_azure.serve_app_svc(app_svc_path)
mocked_azure.setup()

# expose as azure.app.server, .socketio and .api

server   = mocked_azure.server
socketio = mocked_azure.socketio
api      = mocked_azure.api

import azure.oauth
