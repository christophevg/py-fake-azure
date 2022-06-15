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

logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)
formatter = logging.Formatter(FORMAT, DATEFMT)
logging.getLogger().handlers[0].setFormatter(formatter)

func_app_path = os.environ.get("FUNC_APP", None)
app_svc_path  = os.environ.get("APP_SVC",  None)

logger.debug(f"🏃‍♂️ Running Azure from {func_app_path} + {app_svc_path}")

from azure.mock import MockedAzure

mocked_azure = MockedAzure()
mocked_azure.serve_func_app(func_app_path)
mocked_azure.serve_app_svc(app_svc_path)
mocked_azure.setup()

# expose as azure.app.server, .socketio and .api

server   = mocked_azure.server
socketio = mocked_azure.socketio
api      = mocked_azure.api

import azure.oauth
