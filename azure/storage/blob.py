# basic implementation of storage account service

__version__ = "fake-azure"

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
import operator

import azure.functions as func

class Storage(object):
  def __init__(self):
    self.root = Path(os.environ.get("AZURE_SA", "local_blob_storage"))
    logger.debug(f"🗄  Constructing a fake Storage Account in {self.root}.")
    try:
      with open("storage-queues.json") as fp:
        self.storage_queues = json.load(fp)
      for container, queue in self.storage_queues.items():
        logger.debug(f"🔈 Notifying changes to {container} via {queue}")
    except FileNotFoundError:
      logger.warn("⚠️  No storage queues defined !!!")
      logger.warn("   👉 To map blob events to service bus event queues")
      logger.warn("      create a storage-queues.json configuration.")
      self.storage_queues = {}

    try:
      with open(self.root / "tags.json") as fp:
        self.tags = json.load(fp)
        logger.debug(f"🔈 loaded blob tags")
    except FileNotFoundError:
      self.tags = {}

    self.subscriptions = {}
    self.outbox        = []

    self.notifier = Thread(target=self.run_notifier, args=())
    self.notifier.daemon = True
    self.notifier.start()
    self.pool = Pool(processes=10)

  def run_notifier(self):
    def monitor(f):
      def execute(msg, context):
        try:
          if "context" in f.parameters:
            f(msg, context)
          else:
            f(msg)
        except Exception as e:
          logger.error(f"🚨  While executing function {f.name}...")
          logger.exception(e)
      return execute
      
    logger.debug("🔈 Started Storage Account notifier thread.")
    while True:
      if self.outbox:
        while self.outbox:
          (function, msg) = self.outbox.pop(0)
          context = func.Context()
          context.function_name = function.name
          self.pool.apply_async(monitor(function), [msg, context])
      time.sleep(.1)

  def subscribe(self, queue, function):
    try:
      self.subscriptions[queue].append(function)
    except KeyError:
      self.subscriptions[queue] = [ function ]
    logger.debug(f"🗄  Set up subscription on {queue} for {function}.")

  def add(self, container, filename, data):
    path = self.root / Path(container)
    path.mkdir( parents=True, exist_ok=True )
    with open(path / Path(filename), "wb") as fp:
      fp.write(data)
    logger.debug(f"🗄  Created {filename} in {path}.")
    self.notify(container, filename, len(data))

  def tag(self, container, filename, tags):
    if not container in self.tags:
      self.tags[container] = {}
    self.tags[container][filename] = { k:str(v) for k,v in tags.items() }
    with open(self.root / "tags.json", "w") as fp:
      json.dump(self.tags, fp, indent=2)

  def get_tags(self, container, filename):
    try:
      return self.tags[container][filename]
    except KeyError:
      pass
    return {} 

  def find_blobs_by_tags(self, exp):
    # basic exp parsing of "container and 1 tag expression", strictly formatted!
    # e.g. @container = 'mycontainer' AND Name = 'C'
    # e.g. @container = 'mycontainer' AND TimeToSend <= '1666519548'
    container = None
    tag       = None
    value     = None
    parts = exp.split(" AND ")
    for part in parts:
      op = operator.eq
      symbol = "="
      if "<=" in part:
        op = operator.lt
        symbol = "<="
      if ">=" in part:
        op = operator.gt
        symbol = ">="
      k, v = part.split(f" {symbol} ")
      if k == '@container':
        container = v[1:-1]
      else:
        tag   = k[1:-1]
        value = v[1:-1]
    logger.debug(f"🔎 looking in {container} for {tag} {symbol} {value}")
    try:
      for filename in self.tags[container]:
        logger.debug(f" - {filename} : {self.tags[container][filename]}")
        if tag in self.tags[container][filename]:
          logger.debug(f"    {self.tags[container][filename][tag]} {op} {value}")
          if op(self.tags[container][filename][tag], value):
            logger.debug(f"      match!")
            yield BlobProperties(container, filename, self.tags[container][filename])
    except KeyError:
      pass

  def notify(self, container, filename, size):
    queue = self.storage_queues.get(container, None)
    if not queue:
      logger.warn(f"⚠️ No queue for {container}")
      return
    subscriptions = self.subscriptions.get(queue, None)
    if not subscriptions:
      logger.warn(f"⚠️ No subscription on {queue}")
      return
    for function in subscriptions:
      logger.debug(f"🔈 Notifying {function}")
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
      for filename in files:
        try:
          tags = self.tags[container][filename]
        except KeyError:
          tags = {}
        yield BlobProperties(container, filename, tags)

  def get(self, container, filename):
    path = self.root / Path(container)
    path.mkdir( parents=True, exist_ok=True )
    with open(path / Path(filename), "rb") as fp:
      return StorageStreamDownloader(fp.read())

  def exists(self, container, filename):
    path = self.root / Path(container)
    path.mkdir( parents=True, exist_ok=True )
    return (path / Path(filename)).is_file()

StorageAccount = Storage()

class BlobProperties(object):
  def __init__(self, container, name, tags):
    self.container = container
    self.name      = name
    self.tags      = tags

class BlobClient(object):
  def __init__(self, name, container):
    self.name = name
    self.container = container
  
  def upload_blob(self, data, tags=None, overwrite=True):
    StorageAccount.add(self.container, self.name, data)
    if tags:
      self.set_blob_tags(tags)

  def set_blob_tags(self, tags):
    StorageAccount.tag(self.container, self.name, tags)

  def get_blob_tags(self):
    return StorageAccount.get_tags(self.container, self.name)

  def exists(self):
    return StorageAccount.exists(self.container, self.name)

class StorageStreamDownloader(object):
  def __init__(self, data):
    self.data = data

  def readall(self):
    return self.data

  def download_to_stream(self, stream):
    stream.write(self.data)

class ContainerClient(object):
  def __init__(self, container):
    self.container = container
  
  def list_blobs(self):
    return StorageAccount.list(self.container)

  def download_blob(self, filename):
    return StorageAccount.get(self.container, filename)

  def get_blob_client(self, filename):
    return BlobClient(filename, self.container)

class BlobServiceClient(object):
  @classmethod
  def from_connection_string(cls, connection_string):
    return BlobServiceClient()

  def get_container_client(self, container):
    return ContainerClient(container)

  def find_blobs_by_tags(self, exp):
    return StorageAccount.find_blobs_by_tags(exp)

class BlockBlobService():
  def __init__(self, account_name=None, account_key=None):
    pass

  def generate_blob_shared_access_signature(self,
    container_name, blob_name, permission, until):
    return "something"

  def make_blob_url(self, container_name, blob_name, sas_token=None):
    return f"http://localhost:5000/unknown/{container_name}/{blob_name}"

class BlobPermissions():
  ADD    = 0
  CREATE = 1
  DELETE = 2
  READ   = 4
  WRITE  = 8
