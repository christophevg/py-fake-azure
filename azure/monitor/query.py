class LogsQueryClient() :
  def __init__(self, credential):
    pass

  def query_workspace(self, workspace_id, query, timespan=None):
    return LogsQuerResponse()

class MetricsQueryClient():
  def __init__(self, credential):
    pass

class LogsQueryStatus():
  PARTIAL = 1
  SUCCESS = 2

class LogsQueryResponse():
  def __init__(self):
    self.status = LogsQueryStatus.SUCCESS
    self.tables = []
    
    self.partial_error = None
    self.partial_data = None
