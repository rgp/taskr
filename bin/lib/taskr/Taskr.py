import yaml, sys, logging, time, operator
from termcolor import colored
from prettytable import PrettyTable
from os.path import expanduser
from os.path import isdir
from os import mkdir
import hashlib
from Utils import Utils
from Exceptions import *

class Taskr():

  tags = {}

  taskslog_name = "task_log"
  errorlog = "error.log"
  taskr_path = ".taskr/"

  colors = {
      0:"grey",
      1:"red",
      2:"green",
      3:"yellow",
      4:"blue",
      5:"magenta",
      6:"cyan",
      7:"white"
      }
  
  def __init__(self):
    home = expanduser("~") + "/"
    if not isdir(home+".taskr"):
      mkdir(home + ".taskr") 
    self.root = home + self.taskr_path
    logging.basicConfig(filename=self.root + self.errorlog, level=logging.DEBUG)
    self.taskslog_path = self.root + self.taskslog_name
    try:
      self.log = open(self.taskslog_path,"r+")
    except IOError as ioe:
      self.log = open(self.taskslog_path,"w+")
    except Exception as e:
      print "Unexpected error ocurred"
      logging.error(e)
      sys.exit(1)

    self.__loadtasks()
    self.log.close()

  def __loadtasks(self):
    try:
      Task.load_all(self.log) or []
    except Exception as e:
      print "Error loading tasks"
      logging.error(e)
      sys.exit(1)

  def saveTasks(self):
    try:
      self.log = open(self.taskslog_path,"w+")
      self.log.write(yaml.dump(Task.tasks))
      self.log.close()
    except IOError as ioe:
      print "Error while saving"
      logging.error(e)
      sys.exit(1)

  @staticmethod
  def colorTags(tag):
    if tag not in Taskr.tags:
      cindex = len(Taskr.tags) % 8
      Taskr.tags[tag] = colored(tag,Taskr.colors[cindex])
    return Taskr.tags[tag]

  def __tableHeader(self):
    return PrettyTable(["ID","Task","Tag","Last Worked On","Curr session","Total time","Status"])

  def __tablefullHeader(self):
    return PrettyTable(["ID","Task","Tag","Sessions","Last Worked On","Curr session","Total time","Status"])

  def printTasks(self,all=False):
    if len(Task.tasks) > 0:
      print "Your current task log:"
      output = self.__tableHeader()
      output.align["Task"]
      Taskr.tags["-"] = Taskr.colorTags("-")
      for task in Task.tasks[:5] if not all else Task.tasks:
        output.add_row(task.to_row())
      print output.get_string(border=False)
    else:
      print "You currently don't have any registered tasks"

  def taskInfo(self,tid):
    try:
      task = Task.find(tid)
      self.printTask(task)
    except Exception as e:
      print e

  def printTask(self,task=None):
    if task is None:
      return False
    output = self.__tablefullHeader()
    output.align["Task"]
    output.add_row(task.to_row(True))
    print output.get_string(border=False)

  def closeCurrentTask(self):
    try:
      last_task = Task.tasks[-1]
      if last_task.close():
        task_count = len(Task.tasks)
        if task_count > 1:
          Task.tasks.pop()
          i = -1
          while -task_count < i is not None and Task.tasks[i].status != 0:
            i = i - 1
          Task.tasks.insert(i+1,last_task) if i != -1 else Task.tasks.append(last_task)
        self.printTask(last_task)
      else:
        raise TaskNotFoundException("")
    except TaskNotFoundException as nte:
      raise TaskNotFoundException("")
    except IndexError as ie:
      pass
    except Exception as e:
      print e

  def pauseCurrentTask(self):
    try:
      last_task = Task.tasks[-1]
      last_task.pause()
    except IndexError as ie:
      raise TaskNotFoundException("")


  # TODO
  def openTask(self,task_id=None):
    try:
      self.pauseCurrentTask()
    except TaskNotFoundException as nte:
      pass
    try:
      task = Task.find(task_id)
      if task["status"] == 0:
        task["status"] = 1
        task["worklog"][int(time.time())] = {"duration":0}
        Task.tasks.remove(task)
        Task.tasks.append(task)
        print "Reopened task: "+task_id
    except Exception as e:
      print colored("No task found by id: " + str(task_id),"cyan")
      self.printTasks()

  # TODO
  def resumeCurrentTask(self,task_id=True):
    try:
      last_task = Task.find(task_id) if task_id != True else Task.tasks[-1]
      last_task.resume()
    except Exception as e:
      print e
      print colored("No paused task","cyan")
      self.printTasks()


  # TODO
  def deleteTask(self,task_id=True):
    try:
      if task_id != True:
        last_task = Task.find(task_id)
      else:
        raise TaskNotFoundException("")
      Task.tasks.remove(last_task)
    except Exception as e:
      print colored("Couldn't delete task","cyan")
      self.printTasks()

  # Complete
  def newTask(self, name=None, estimated=None, tag=""):
    name = colored("Untitled","red") if name == None else name
    estimated = 0.0 if estimated == None else estimated
    try:
      self.pauseCurrentTask()
    except TaskNotFoundException as nte:
      pass
    Task.tasks.append(Task({
      "name": name,
      "tag": tag,
      "estimated": estimated,
      }))


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

class Task(yaml.YAMLObject):

  tasks = [] # Task Array (Static element)

  id = ""
  name = ""
  location = ""
  tag = "-"
  estimated = 0.0
  status = 3 # Pending
# status: 1 | 2 | 3 | 0      -> 1 active, 2 paused, 3 pending, 0 closed
  elapsed = 0
  worklog = [] # WorkSession Array

  def __init__(self, info):
    self.id = hashlib.sha1(info["name"] + " " + str(int(time.time()))).hexdigest()
    self.name = info["name"]
    self.tag = info["tag"]
    self.estimated = info["estimated"]

  def start(self):
    self.status = 1
    self.worklog = [WorkSession()]
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
          return [self.id[0:8],self.name,self.tag,len(self.worklog), Utils.datefmt(last_session.start_time), cur_sess_time, total_time, Utils.readableStatus[self.status]]
        else:
          return [self.id[0:8],self.name,Taskr.colorTags(self.tag), Utils.datefmt(last_session.start_time), cur_sess_time, total_time, Utils.readableStatus[self.status]]
      else:
        if with_sessions:
          return [self.id[0:8],self.name,self.tag,len(self.worklog),"-", 0, 0, Utils.readableStatus[self.status]]
        else:
          return [self.id[0:8],self.name,self.tag,"-", Utils.hourstohuman(0), Utils.hourstohuman(0), Utils.readableStatus[self.status]]

  @staticmethod
  def load_all(tasklog):
    try:
      Task.tasks = yaml.load(tasklog) or []
      return Task.tasks
    except Exception as e:
      print "Error loading tasks"
      logging.error(e)
      sys.exit(1)

  @staticmethod
  def find(taskid):
    if len(Task.tasks) == 0:
      raise NoTasksException()
    else:
      for element in Task.tasks:
        if element.id[0:8] == str(taskid):
          return element
      exm = "Task "+str(tid)+" not found"
      raise TaskNotFoundException(exm)

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
