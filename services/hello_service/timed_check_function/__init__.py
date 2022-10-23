import logging
logger = logging.getLogger(__name__)

import os
import time

from azure.storage.blob import BlobServiceClient

import azure.functions as func

client = BlobServiceClient.from_connection_string(os.getenv("CONNECTIONSTRING"))

def main(mytimer: func.TimerRequest):
  now = int(time.time())
  blobs = client.find_blobs_by_tags(f"@container = 'todo' AND \"tts\" <= '{now}'")
  for prop in blobs:
    logger.info(f"`🔔 {prop.name} is due, adding 15s to {now}")
    blob = client.get_container_client("todo").get_blob_client(prop.name)
    blob.set_blob_tags({ "tts": now + 15 })
