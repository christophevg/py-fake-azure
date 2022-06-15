# basic implementation of storage account service

import logging
logger = logging.getLogger(__name__)

import os
import json

from pathlib import Path
from threading import Thread
from multiprocessing.dummy import Pool
from datetime import datetime
import time
import uuid

import azure.functions as func

class Storage(object):
  def __init__(self):
    self.root = Path(os.environ.get("AZURE_SA", "local_blob_storage"))
    try:
      with open("storage-queues.json") as fp:
        self.storage_queues = json.load(fp)
    except FileNotFoundError:
      logger.warn("no storage queues defined")
      self.storage_queues = {}
    self.subscriptions = {}
    self.outbox = []

    self.notifier = Thread(target=self.run_notifier, args=())
    self.notifier.daemon = True
    self.notifier.start()
    self.pool = Pool(processes=10)

  def run_notifier(self):
    logger.info("started SA notifier...")
    while True:
      if self.outbox:
        while self.outbox:
          (function, msg) = self.outbox.pop(0)
          self.pool.apply_async(function, [msg])
      time.sleep(.1)

  def subscribe(self, queue, function):
    try:
      self.subscriptions[queue].append(function)
    except KeyError:
      self.subscriptions[queue] = [ function ]
    logger.info(f"added subscription on {queue} for {function}")

  def add(self, container, filename, data):
    path = self.root / Path(container)
    path.mkdir( parents=True, exist_ok=True )
    with open(path / Path(filename), "wb") as fp:
      fp.write(data)
    logger.debug(f"created {filename} in {path}")
    self.notify(container, filename, len(data))

  def notify(self, container, filename, size):
    queue = self.storage_queues.get(container, None)
    if not queue: return
    subscriptions = self.subscriptions.get(queue, None)
    if not subscriptions: return
    for function in subscriptions:
      logger.debug(f"notifying {function}")
      self.outbox.append((function, func.ServiceBusMessage({
        "topic": "...",
        "subject": f"/blobServices/default/containers/{container}/blobs/{filename}",
        "eventType": "Microsoft.Storage.BlobCreated",
        "id": str(uuid.uuid4()),
        "data": {
          "api": "PutBlockList",
          "clientRequestId": str(uuid.uuid4()),
          "requestId": str(uuid.uuid4()),
          "eTag": "...",
          "contentType": "application/octet-stream",
          "contentLength": size,
          "blobType": "BlockBlob",
          "url": f"https://fake.blob.core.windows.net/{container}/{filename}",
          "sequencer": "...",
          "storageDiagnostics": {
            "batchId": "..."
          }
        },
        "dataVersion": "",
        "metadataVersion": "1",
        "eventTime": datetime.utcnow().isoformat()
      })))

  def list(self, container):
    path = self.root / Path(container)
    for _, _, files in os.walk(path):
      return [ Blob(f, container=container) for f in files ]

  def get(self, container, filename):
    path = self.root / Path(container)
    path.mkdir( parents=True, exist_ok=True )
    with open(path / Path(filename), "rb") as fp:
      return StorageStreamDownloader(fp.read())

StorageAccount = Storage()

class Blob(object):
  def __init__(self, name, container):
    self.name = name
    self.container = container
  
  def upload_blob(self, data):
    StorageAccount.add(self.container, self.name, data)

class StorageStreamDownloader(object):
  def __init__(self, data):
    self.data = data

  def readall(self):
    return self.data

class ContainerClient(object):
  def __init__(self, container):
    self.container = container
  
  def list_blobs(self):
    return StorageAccount.list(self.container)

  def download_blob(self, filename):
    return StorageAccount.get(self.container, filename)

  def get_blob_client(self, filename):
    return Blob(filename, self.container)

class BlobServiceClient(object):
  @classmethod
  def from_connection_string(cls, connection_string):
    return BlobServiceClient()

  def get_container_client(self, container):
    return ContainerClient(container)
