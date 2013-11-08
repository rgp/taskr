#
# name: "Tarea 1"
# id: 1
# status: 1 | 2 | 0      -> 1 active, 2 paused, 0 closed
# worklog:
#   -
#     started_at: 1383167335
#     duration: 3
#   -
#     started_at: 1383181735
#     duration: 1

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
      self.tasks = yaml.load(self.log) or []
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
    return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')

  def __roundup(self,number,decimals):
    val = pow(10,decimals)
    return ceil(number * val) / val

  def __hourstohuman(self,time):
    dec = (time - int(time))
    minutes = self.__roundup(dec*60,0)
    hours = self.__roundup(time - dec,2)
    return str(int(hours))+"h "+str(int(minutes))+"m"

  def __preparerow(self,task):
    last_session_time = max(task["worklog"].iteritems(), key=operator.itemgetter(0))[0]
    cur_sess_time = self.__roundup((time.time()-last_session_time)/3600,2) if task["status"] == 1 else 0
    total_time = self.__roundup(task["elapsed"] + cur_sess_time,2) if task["status"] == 1 else task["elapsed"]
    cur_sess_time = self.__hourstohuman(cur_sess_time)
    total_time = self.__hourstohuman(total_time)
    return [str(task["id"])[0:8],task["name"],len(task["worklog"]), self.__datefmt(last_session_time), cur_sess_time, total_time, self.readableStatus[task["status"]]]

  def printTasks(self,all=False):
    if len(self.tasks) > 0:
      print "Your current task log:"
      output = PrettyTable(["ID","Task","Sessions","Last Worked On","Curr session","Total time","Status"])
      output.align["Task"]
      for task in self.tasks[-5:] if not all else self.tasks:
        output.add_row(self.__preparerow(task))
      print output.get_string(border=False)
    else:
      print "You currently don't have any registered tasks"

  def printTask(self,task=None):
    if task is None:
      return False
    output = PrettyTable(["ID","Task","Sessions","Last Worked On","Current session","Total time","Status"])
    output.align["Task"]
    output.add_row(self.__preparerow(task))
    print output.get_string(border=False)

  def closeCurrentTask(self):
    try:
      if self.tasks[-1]["status"] == 1:
        last_task = self.tasks[-1]
        last_task["status"] = 0
        self.__stopCurrentSession(last_task)
        self.tasks.pop()
        i = -1
        while self.tasks[i] is not None and self.tasks[i]["status"] != 0:
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
      if self.tasks[-1]["status"] == 1:
        last_task = self.tasks[-1]
        last_task["status"] = 2
        self.__stopCurrentSession(last_task)
      else:
        raise NoTaskException("")
    except IndexError as ie:
      pass

  def __findtask(self,tid):
    tasks = [element for element in self.tasks if str(element['id'])[0:8] == str(tid)]
    if len(tasks) > 1:
      raise Exception("Duplicate task id")
    elif len(tasks) < 1:
      raise Exception("Task not found")
    else:
      return tasks[0]

  def openTask(self,task_id=None):
    try:
      self.pauseCurrentTask()
    except NoTaskException as nte:
      pass
    try:
      task = self.__findtask(int(task_id))[-1]
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
      last_task = self.__findtask(int(task_id))[-1] if task_id != True else self.tasks[-1]
      if last_task["status"] == 0:
        raise Exception("")
      else:
        self.tasks.remove(last_task)
        self.tasks.append(last_task)
        last_task["status"] = 1
        last_task["worklog"][int(time.time())] = {"duration":0}
    except Exception as e:
      print colored("No paused task","cyan")
      self.printTasks()

  def __stopCurrentSession(self,last_task):
    last_session_time = max(last_task["worklog"].iteritems(), key=operator.itemgetter(0))[0]
    last_session = last_task["worklog"][last_session_time]
    last_session["duration"] = (time.time() - last_session_time) / 3600
    last_task["elapsed"] = last_task["elapsed"] + last_session["duration"]

  def deleteTask(self,task_id=True):
    try:
      if task_id != True:
        last_task = self.__findtask(task_id)[-1]
      else:
        raise NoTaskException("")
      self.tasks.remove(last_task)
    except Exception as e:
      print colored("Couldn't delete task","cyan")
      self.printTasks()

  def newTask(self, name=None, estimated=None):
    name = colored("Untitled","red") if name == None else name
    estimated = 0.0 if estimated == None else estimated
    try:
      self.pauseCurrentTask()
    except NoTaskException as nte:
      pass
    self.tasks.append(
        {
          "name" : name,
          "id" : hashlib.sha1(name + " " + str(int(time.time()))).hexdigest(),
          "estimated" : estimated,
          "elapsed" : 0,
          "status" : 1,
          "worklog" : {int(time.time()):{"duration":0}}
          }
        )

class NoTaskException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)
