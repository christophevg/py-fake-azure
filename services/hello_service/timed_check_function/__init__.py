import logging
logger = logging.getLogger(__name__)

import os
import time

from azure.storage.blob import BlobServiceClient

import azure.functions as func

client = BlobServiceClient.from_connection_string(os.getenv("CONNECTIONSTRING"))

backoff = [ 5, 10, 15 ]

def main(mytimer: func.TimerRequest):
  now = int(time.time())
  blobs = client.find_blobs_by_tags(f"@container = 'todo' AND \"tts\" <= '{now}'")
  for prop in blobs:
    logger.info(f"🔔 {prop.name} is due ({prop.tags}")
    tags = prop.tags
    if "retries" in prop.tags:
      retries = int(prop.tags["retries"]) + 1
      try:
        next_retry = now + backoff[retries]
        tags["tts"]     = next_retry
        tags["retries"] = retries
        logger.info(f"  ✌️ retrying for {retries} time @ {next_retry}")
      except:
        # no more retries: we're done
        logger.info(f"  🛑 {retries} retries, we're done.")
        tags["tts"]    = "no"
        tags["status"] = "done"
    else:
      logger.info("  ☝️ first attempt")
      tags["retries"] = 0
      tags["tts"]     = now + backoff[0]

    blob = client.get_container_client("todo").get_blob_client(prop.name)
    blob.set_blob_tags(tags)
