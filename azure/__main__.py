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

import fire

from azure.mock import MockedAzure

from azure.map import generate

class Mapper(object):
  def __init__(self):
    pass

  def map(self, path, outfile, format="png"):
    generate(path, outfile, format)

if __name__ == '__main__':
  fire.Fire(MockedAzure)
