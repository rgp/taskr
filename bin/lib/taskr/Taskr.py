import yaml, sys, logging
from termcolor import colored
from prettytable import PrettyTable
from os.path import expanduser
from os.path import isdir
from os import mkdir
from Utils import Utils
from Exceptions import *
from Task import Task
from WorkSession import WorkSession

class Taskr():

  taskslog_name = "task_log"
  errorlog = "error.log"
  taskr_path = ".taskr/"
  root = "."

  def __init__(self):
    home = expanduser("~") + "/"
    if not isdir(home+".taskr"):
      mkdir(home + ".taskr") 
    Taskr.root = home + self.taskr_path
    logging.basicConfig(filename=Taskr.root + self.errorlog, level=logging.DEBUG)
    self.taskslog_path = Taskr.root + self.taskslog_name
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
      Taskr.load_all(self.log) or []
    except Exception as e:
      print "Error loading tasks"
      logging.error(e)
      sys.exit(1)

  def saveTasks(self):
    try:
      self.log = open(self.taskslog_path,"w+")
      self.log.write(yaml.dump(Taskr.tasks))
      self.log.close()
    except IOError as ioe:
      print "Error while saving"
      logging.error(e)
      sys.exit(1)

  @staticmethod
  def load_all(tasklog):
    try:
      Taskr.tasks = yaml.load(tasklog) or []
      return Taskr.tasks
    except Exception as e:
      print e
      print "Error loading tasks"
      logging.error(e)
      sys.exit(1)

  @staticmethod
  def find(taskid):
    if len(Taskr.tasks) == 0:
      raise NoTasksException()
    else:
      for element in Taskr.tasks:
        if element.id[0:8] == str(taskid):
          return element
      exm = "Task "+str(taskid)+" not found"
      raise TaskNotFoundException(exm)

  def printTask(self,task=None):
    if task is None:
      return False
    output = Utils.tableHeader(True)
    output.align["Task"]
    Utils.tags["-"] = Utils.colorTags("-")
    output.add_row(task.to_row(True))
    print output.get_string(border=False)

  def printTasks(self,all=False,detailed=False):
    if len(Taskr.tasks) > 0:
      print "Your current task log:"
      output = Utils.tableHeader(detailed)
      output.align["Task"]
      Utils.tags["-"] = Utils.colorTags("-")
      for task in Taskr.tasks[-5:] if not all else Taskr.tasks:
        output.add_row(task.to_row(detailed))
      print output.get_string(border=False)
    else:
      print "You currently don't have any registered tasks"

  def taskInfo(self,specific_task = False):
    try:
      if specific_task:
        task = Taskr.find(specific_task)
        self.printTask(task)
      else:
        self.printTasks(True,True)
    except Exception as e:
      print e

  def closeCurrentTask(self):
    try:
      last_task = Taskr.tasks[-1]
      if last_task.close():
        task_count = len(Taskr.tasks)
        if task_count > 1:
          Taskr.tasks.pop()
          i = -1
          while -task_count < i is not None and Taskr.tasks[i].status != 0:
            i = i - 1
          Taskr.tasks.insert(i+1,last_task) if i != -1 else Taskr.tasks.append(last_task)
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
      last_task = Taskr.tasks[-1]
      last_task.pause()
    except IndexError as ie:
      raise TaskNotFoundException("")

  def renewTaskAt(self,when):
    try:
      last_task = Taskr.tasks[-1]
      last_task.renewAt(when)
    except IndexError as ie:
      raise TaskNotFoundException("")

  # TODO
  def openTask(self,task_id=None):
    try:
      self.pauseCurrentTask()
    except TaskNotFoundException as nte:
      pass
    try:
      task = Taskr.find(task_id)
      if task.status == 0:
        task.status = 1
        task.start()
        Taskr.tasks.remove(task)
        Taskr.tasks.append(task)
        print "Reopened task: "+task_id
    except Exception as e:
      print colored("No task found by id: " + str(task_id),"cyan")
      self.printTasks()

  # TODO
  def resumeCurrentTask(self,task_id=True):
    try:
      last_task = Taskr.find(task_id) if task_id != True else Taskr.tasks[-1]
      last_task.resume()
    except Exception as e:
      print e
      print colored("No paused task","cyan")
      self.printTasks()

  # TODO
  def deleteTask(self,task_id=True):
    try:
      if task_id != True:
        last_task = Taskr.find(task_id)
      else:
        raise TaskNotFoundException("")
      Taskr.tasks.remove(last_task)
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
    t = Task({ "name": name, "tag": tag, "estimated": estimated, })
    t.start()
    Taskr.tasks.append(t)
