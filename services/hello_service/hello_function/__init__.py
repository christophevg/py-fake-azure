__version__ = "1.0.0"

import logging
logger = logging.getLogger(__name__)

def main(req):
  name = req.params.get("name")
  logger.info(f"version: {__version__} / name: {name}");

  if name:
    return f"Hello, {name}.\n"
  else:
    return "Hello.\n"
