class NoLastSessionException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)

class NoTasksException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)

class DuplicateTaskException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)

class TaskNotFoundException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)
