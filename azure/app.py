import logging
logger = logging.getLogger(__name__)

import schedule
from threading import Thread
import time

# create thread for scheduler
def run_scheduler():
  while True:
    logger.debug("⏰ tick")
    schedule.run_pending()
    time.sleep(1)
  
scheduler = Thread(target=run_scheduler, args=())
scheduler.daemon = True
scheduler.start()

import os

# load the environment variables for this setup
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "DEBUG"

# setup logging infrastructure

logging.getLogger("urllib3").setLevel(logging.WARN)
logging.getLogger("graphviz").setLevel(logging.WARN)
logging.getLogger("schedule").setLevel(logging.WARN)

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
logger.info(f"🏃‍♂️ Running Azure with:")
if common_path:
  logger.info(f"🍪 common path {common_path}")
  mocked_azure.with_common(common_path)

logger.info(f"📚 Function Apps")
for path in func_app_paths:
  logger.info(f"  📗 adding function app from {path}")
  mocked_azure.serve_func_app(path)

logger.info(f"🌎 App Service from {app_svc_path}")
mocked_azure.serve_app_svc(app_svc_path)
mocked_azure.setup()

# expose as azure.app.server, .socketio and .api

server   = mocked_azure.server
socketio = mocked_azure.socketio
api      = mocked_azure.api

import azure.oauth
