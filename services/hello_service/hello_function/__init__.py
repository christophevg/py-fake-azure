import logging
logger = logging.getLogger(__name__)

def main(req, outputblob):
  logger.info(f"❤️  Function {__name__} received a request...");

  name = req.params.get("name")

  if name:
    outputblob.set(str.encode(name))
    return f"Hello, {name}.\n"
  else:
    outputblob.set(str.encode("no name provided"))
    return "Hello.\n"
