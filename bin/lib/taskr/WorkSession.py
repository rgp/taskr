import yaml, time
from Utils import Utils
class WorkSession(yaml.YAMLObject):
  start_time = 0
  end_time = 0
  duration = 0

  def __init__(self):
    self.id = self.start_time = int(time.time())
    self.end_time = None
    self.duration = 0

  def stop(self):
    self.end_time = int(time.time())
    self.duration = (self.end_time - self.start_time) / 3600
    return self.duration

  def current_time(self):
    return Utils.roundup((time.time()-self.start_time)/3600,2)
