#
# name: "Tarea 1"
# id: 1
# status: 1 | 2 | 3 | 0      -> 1 active, 2 paused, 3 pending, 0 closed
# tag: ""
# worklog:
#   -
#     started_at: 1383167335
#     duration: 3
#   -
#     started_at: 1383181735
#     duration: 1

# - elapsed: 0
#   estimated: 0.0
#   id: 00c870934d0ec536bb886cb2b20818a35cdef1ec
#   name: aasads
#   status: 1
#   tag: null
#   worklog:
#     1403845568: {duration: 0,end_time: 0}
#     1403845569: {duration: 0,end_time: 0}
#     1403845570: {duration: 0,end_time: 0}
#     1403845571: {duration: 0,end_time: 0}
import yaml, hashlib, time
from WorkSession import WorkSession
from Utils import Utils
class Task(yaml.YAMLObject):


  def __init__(self, info):
    # default values 
    self.id = ""
    self.name = ""
    self.tag = "-"
    self.estimated = 0.0
    self.status = 3 # Pending
  # self.status: 1 | 2 | 3 | 0      -> 1 active, 2 paused, 3 pending, 0 closed
    self.elapsed = 0

    self.id = hashlib.sha1(info["name"] + " " + str(int(time.time()))).hexdigest()
    self.name = info["name"]
    self.tag = info["tag"]
    self.estimated = info["estimated"]
    self.worklog = [] # WorkSession Array


  def start(self):
    self.status = 1
    w = WorkSession()
    self.worklog = self.worklog + [w]
    return True

  def pause(self):
    self.status = 2
    self.__stopCurrentSession()
    return True

  def close(self):
    if self.status != 0:
      self.status = 0
      self.__stopCurrentSession()
      return True
    else:
      return False

  def resume(self):
    if self.status >= 2:
      self.status = 1
      w = WorkSession()
      self.worklog = self.worklog + [w]
      return True
    elif self.status == 0:
      raise Exception("Closed task")
    else:
      return False

  def renewAt(self,when):
    last_session = self.last_session()
    if last_session:
      self.elapsed = self.elapsed + last_session.stop(when)
    w = WorkSession()
    self.worklog = self.worklog + [w]

  def __stopCurrentSession(self):
    last_session = self.last_session()
    if last_session:
      self.elapsed = self.elapsed + last_session.stop()

  def last_session(self):
    if len(self.worklog) > 0:
      self.worklog.sort(key=lambda x: x.id) # I belive this is unnecesary
      return self.worklog[-1] 
    else:
      return False

  def to_row(self,with_sessions = False):
      last_session = self.last_session()
      if last_session:
        cur_sess_time = last_session.current_time() if self.status == 1 else 0
        total_time = Utils.roundup(self.elapsed + cur_sess_time,2) if self.status == 1 else self.elapsed
        cur_sess_time = Utils.hourstohuman(cur_sess_time)
        total_time = Utils.hourstohuman(total_time)
        if with_sessions:
          return [self.id[0:8],self.name,Utils.colorTags(self.tag),len(self.worklog), Utils.datefmt(last_session.start_time), cur_sess_time, total_time, Utils.readableStatus[self.status]]
        else:
          return [self.id[0:8],self.name,Utils.colorTags(self.tag), Utils.datefmt(last_session.start_time), cur_sess_time, total_time, Utils.readableStatus[self.status]]
      else:
        if with_sessions:
          return [self.id[0:8],self.name,Utils.colorTags(self.tag),len(self.worklog),"-", 0, 0, Utils.readableStatus[self.status]]
        else:
          return [self.id[0:8],self.name,Utils.colorTags(self.tag),"-", Utils.hourstohuman(0), Utils.hourstohuman(0), Utils.readableStatus[self.status]]
