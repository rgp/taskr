import yaml, sys, logging, time, datetime, operator
from termcolor import colored
from math import ceil
from prettytable import PrettyTable
from os.path import expanduser
from os.path import isdir
from os import mkdir
import hashlib

class Taskr():

  taskslog_name = "task_log"
  errorlog = "error.log"
  taskr_path = ".taskr/"
  readableStatus = {
      0:colored("Closed","cyan"),
      1:colored("Active","green"),
      2:colored("Paused","yellow",None,["blink"])}
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
    self.tags = {}
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
      self.tasks = Task.load_all(self.log) or []
    except Exception as e:
      print "Error loading tasks"
      logging.error(e)
      sys.exit(1)

  def saveTasks(self):
    try:
      self.log = open(self.taskslog_path,"w+")
      self.log.write(yaml.dump(self.tasks))
      self.log.close()
    except IOError as ioe:
      print "Error while saving"
      logging.error(e)
      sys.exit(1)

  def __datefmt(self,time):
    return datetime.datetime.fromtimestamp(time).strftime('%y-%m-%d %H:%M')

  def __roundup(self,number,decimals):
    val = pow(10,decimals)
    return ceil(number * val) / val

  def __hourstohuman(self,time):
    dec = (time - int(time))
    minutes = self.__roundup(dec*60,0)
    hours = self.__roundup(time - dec,2)
    return str(int(hours))+"h "+str(int(minutes))+"m"

  def __tableHeader(self):
    return PrettyTable(["ID","Task","Tag","Last Worked On","Curr session","Total time","Status"])

  def __colorTags(self,tag):
    if tag not in self.tags:
      cindex = len(self.tags) % 8
      self.tags[tag] = colored(tag,self.colors[cindex])
    return self.tags[tag]

  def __preparerow(self,task):
    try:
      last_session = task.last_session()
      cur_sess_time = self.__roundup((time.time()-last_session.start_time)/3600,2) if task.status == 1 else 0
      total_time = self.__roundup(task.elapsed + cur_sess_time,2) if task.status == 1 else task.elapsed
      cur_sess_time = self.__hourstohuman(cur_sess_time)
      total_time = self.__hourstohuman(total_time)
    except NoLastSessionException:
      return [str(task.id)[0:8],task.name,task.tag,len(task.worklog),"-", 0, 0, self.readableStatus[task.status]]
    return [str(task.id)[0:8],task.name,self.__colorTags(task.tag), self.__datefmt(last_session.start_time), cur_sess_time, total_time, self.readableStatus[task.status]]

  def __tablefullHeader(self):
    return PrettyTable(["ID","Task","Tag","Sessions","Last Worked On","Curr session","Total time","Status"])

  def __preparefullrow(self,task):
    try:
      last_session = task.last_session()
      last_session_time = last_session.start_time
      cur_sess_time = self.__roundup((time.time()-last_session_time)/3600,2) if task["status"] == 1 else 0
      total_time = self.__roundup(task["elapsed"] + cur_sess_time,2) if task["status"] == 1 else task["elapsed"]
      cur_sess_time = self.__hourstohuman(cur_sess_time)
      total_time = self.__hourstohuman(total_time)
    except NoLastSessionException:
      return [str(task.id)[0:8],task.name,task.tag,len(task.worklog),"-", 0, 0, self.readableStatus[task.status]]
    return [str(task.id)[0:8],task.name,task.tag,len(task.worklog), self.__datefmt(last_session.start_time), cur_sess_time, total_time, self.readableStatus[task.status]]

  def printTasks(self,all=False):
    if len(self.tasks) > 0:
      print "Your current task log:"
      output = self.__tableHeader()
      output.align["Task"]
      self.tags["-"] = self.__colorTags("-")
      for task in self.tasks[:5] if not all else self.tasks:
        output.add_row(self.__preparerow(task))
      print output.get_string(border=False)
    else:
      print "You currently don't have any registered tasks"

  def taskInfo(self,tid):
    try:
      task = self.__findtask(tid)[-1]
      self.printTask(task)
    except Exception as e:
      print e

  def printTask(self,task=None):
    if task is None:
      return False
    output = self.__tablefullHeader()
    output.align["Task"]
    output.add_row(self.__preparefullrow(task))
    print output.get_string(border=False)

  def closeCurrentTask(self):
    try:
      if self.tasks[-1].status == 1:
        last_task = self.tasks[-1]
        last_task.status = 0
        self.__stopCurrentSession(last_task)
        self.tasks.pop()
        i = -1
        while self.tasks[i] is not None and self.tasks[i].status != 0:
          i = i - 1
        self.tasks.insert(i+1,last_task) if i != -1 else self.tasks.append(last_task)
        self.printTask(last_task)
      else:
        raise NoTaskException("")
    except NoTaskException as nte:
      raise NoTaskException("")
    except IndexError as ie:
      pass
    except Exception as e:
      print e

  def pauseCurrentTask(self):
    try:
      if self.tasks[-1].status == 1:
        last_task = self.tasks[-1]
        last_task.status = 2
        self.__stopCurrentSession(last_task)
      else:
        raise NoTaskException("")
    except IndexError as ie:
      pass

  def __findtask(self,tid):
    tasks = [element for element in self.tasks if str(element.id)[0:8] == str(tid)]
    if len(tasks) > 1:
      raise Exception("Duplicate task id")
    elif len(tasks) < 1:
      exm = "Task "+str(tid)+" not found"
      raise Exception(exm)
    else:
      return tasks[-1]

  def openTask(self,task_id=None):
    try:
      self.pauseCurrentTask()
    except NoTaskException as nte:
      pass
    try:
      task = self.__findtask(task_id)
      if task["status"] == 0:
        task["status"] = 1
        task["worklog"][int(time.time())] = {"duration":0}
        self.tasks.remove(task)
        self.tasks.append(task)
        print "Reopened task: "+task_id
    except Exception as e:
      print colored("No task found by id: " + str(task_id),"cyan")
      self.printTasks()

  def resumeCurrentTask(self,task_id=True):
    try:
      last_task = self.__findtask(task_id) if task_id != True else self.tasks[-1]
      if last_task.status == 0:
        raise Exception("Closed task")
      else:
        self.tasks.remove(last_task)
        self.tasks.append(last_task)
        last_task.status = 1
        last_task.worklog.append(WorkSession(int(time.time()),{"duration":0,"end_time":0}))
    except Exception as e:
      print e
      print colored("No paused task","cyan")
      self.printTasks()

  # Corrected
  def __stopCurrentSession(self,last_task):
    last_session = last_task.last_session()
    last_session.duration = (time.time() - last_session.start_time) / 3600
    last_task.elapsed = last_task.elapsed + last_session.duration

  def deleteTask(self,task_id=True):
    try:
      if task_id != True:
        last_task = self.__findtask(task_id)
      else:
        raise NoTaskException("")
      self.tasks.remove(last_task)
    except Exception as e:
      print colored("Couldn't delete task","cyan")
      self.printTasks()

  def newTask(self, name=None, estimated=None, tag=""):
    name = colored("Untitled","red") if name == None else name
    estimated = 0.0 if estimated == None else estimated
    try:
      self.pauseCurrentTask()
    except NoTaskException as nte:
      pass
    self.tasks.append(Task(
      {
        "name" : name,
        "id" : hashlib.sha1(name + " " + str(int(time.time()))).hexdigest(),
        "tag" : tag,
        "estimated" : estimated,
        "elapsed" : 0,
        "status" : 1,
        "worklog" : {int(time.time()):{"duration":0,"end_time":0}}
        }
      )
      )

class NoLastSessionException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)

class NoTaskException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)

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
  id = ""
  name = ""
  tag = "-"
  estimated = 0.0
  status = 3 # Pending
  elapsed = 0
  worklog = [] # WorkSession Array

  def __init__(self, info):
    self.id = info["id"]
    self.name = info["name"]
    self.tag = info["tag"]
    self.estimated = info["estimated"]
    self.status = info["status"]
    self.elapsed = info["elapsed"]
    w = []
    for _time, _info in info["worklog"].iteritems():
      w.append(WorkSession(_time, _info))
    self.worklog = w

  @staticmethod
  def load_all(tasklog):
    try:
      return yaml.load(tasklog) or []
      # yaml_tasks = yaml.load(tasklog) or []
      # tasks = []
      # for _t in yaml_tasks:
      #   tasks.append(Task(_t))
      # return tasks
    except Exception as e:
      print "Error loading tasks"
      print e
      logging.error(e)
      sys.exit(1)

  def last_session(self):
    if len(self.worklog) > 0:
      self.worklog.sort(key=lambda x: x.id) # I belive this is unnecesary
      return self.worklog[-1] 
    else:
      raise NoLastSessionException("")



class WorkSession(yaml.YAMLObject):
  start_time = 0
  end_time = 0
  duration = 0

  def __init__(self, start_time, info):
    self.id = self.start_time = start_time
    self.end_time = info["end_time"]
    self.duration = info["duration"]
