import yaml, time, subprocess, sys, os, signal
from Utils import Utils
import Taskr

def preexec_function():
    os.setpgrp()

class WorkSession(yaml.YAMLObject):

  def __init__(self):
    # default values
    self.start_time = 0
    self.end_time = None
    self.duration = 0.0
    self.location = ""
    self.pid = None
    self.cwd = os.getcwd()

    self.id = self.start_time = int(time.time())
    encoding = sys.getfilesystemencoding()
    path = os.path.dirname(unicode(__file__, encoding)) + "/../../"
    open_session = subprocess.Popen(["python",path + "tracker.py",str(self.id)],preexec_fn=preexec_function)
    self.pid = open_session.pid

  def stop(self,when = None):
    self.end_time = (int(time.time()) if when is None else when)
    self.duration = float(self.end_time - self.start_time) / 3600
    if self.duration < 0:
      sys.exit(3)
    if hasattr(self, 'pid') and self.pid is not None:
      try:
        os.kill(self.pid, signal.SIGINT)
      except Exception as e:
        pass
      del self.pid 
    return self.duration

  def current_time(self):
    return Utils.roundup((time.time()-self.start_time)/3600,2)

  def to_row(self):
    end_time = Utils.datefmt(self.end_time) if self.end_time is not None else "-"
    start_time = Utils.datefmt(self.start_time)
    duration = Utils.hourstohuman(self.duration)
    cwd = self.cwd if hasattr(self, 'cwd') else "-"
    return ["",start_time,end_time,duration,cwd]
