import logging
logger = logging.getLogger(__name__)

import json

import azure.functions as func
from azure.storage.blob import BlobServiceClient

def main(msg : func.ServiceBusMessage):
  # "subject" : "/blobServices/default/containers/{container}/blobs/{filename}"
  subject   = json.loads(msg.get_body().decode("utf-8"))["subject"].split("/")
  container = subject[-3]
  filename  = subject[-1]
  
  client    = BlobServiceClient.from_connection_string("dummy")
  container = client.get_container_client(container)
  content   = container.download_blob(filename).readall().decode()
  
  logger.info(f"💕 Function {__name__} was informed that someone said hello.");
  logger.info(f"   👉 {content}");
