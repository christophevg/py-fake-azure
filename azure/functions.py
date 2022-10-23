import json
import uuid

class HttpResponse(object):
  def __init__(self, body=None, status_code=None, headers=None, mimetype=None, charset=None):
    self.body        = body
    self.status_code = status_code
    self.headers     = {} if headers is None else headers
    self.mimetype    = mimetype
    self.charset     = charset
  
  def get_body(self):
    return self.body

class ServiceBusMessage(object):
  def __init__(self, body):
    self.body = json.dumps(body).encode()

  def get_body(self):
    return self.body
  
  @property
  def message_id(self):
    return "..."

  @property
  def content_type(self):
    return "application/json"

  @property
  def expiration_time(self):
    return "..."

  @property
  def label(self):
    return "..."

  @property
  def partition_key(self):
    return "..."
    
  @property
  def reply_to(self):
    return "..."

  @property
  def reply_to_session_id(self):
    return "..."

  @property
  def scheduled_enqueue_time(self):
    return "..."

  @property
  def session_id(self):
    return "..."

  @property
  def time_to_live(self):
    return "..."

  @property
  def to(self):
    return "..."

  @property
  def user_properties(self):
    return "..."

  @property
  def metadata(self):
    return "..."

class Context():
  def __init__(self):
    self.function_directory = None
    self.function_name      = None
    self.invocation_id      = str(uuid.uuid4())
    self.trace_context      = None
    self.retry_context      = None
