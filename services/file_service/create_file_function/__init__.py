import logging
logger = logging.getLogger(__name__)

import os
import time

from azure.storage.blob import BlobServiceClient

client = BlobServiceClient.from_connection_string(os.getenv("CONNECTIONSTRING"))

def main(req):
  filename = req.params.get("filename")
  content  = bytes(req.params.get("content"), "utf-8")
  
  container = client.get_container_client("todo")
  blob = container.get_blob_client(filename)
  blob.upload_blob(content, tags={ "tts": str(int(time.time())+10)})
  logger.info("📄 created blob with a tts in 10s")

  return "ok"
