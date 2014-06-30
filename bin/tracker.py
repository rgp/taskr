import os, time, sys, signal
from os.path import expanduser
from sys import stdin
from lib.taskr.Utils import Utils
from lib.taskr.Taskr import Taskr

step = 5
last_checkpoint = current_checkpoint = int(time.time())
wsid = "NOID"
alive=True
path = ""

def signal_handler(signal, frame):
  alive = False
signal.signal(signal.SIGINT, signal_handler)

def open_file():
  wsid = sys.argv[0]
  home = expanduser("~") + "/"
  path = home + Taskr.taskr_path
  return open(path + "tracker.ttmp","w+")
  # return open(path + wsid + ".ttmp","w+")

def write_time(tracking_file):
  tracking_file.seek(0)
  tracking_file.write(str(current_checkpoint))

def read_time(tracking_file):
  # print "read %d" % current_checkpoint
  tracking_file.seek(0)
  last_checkpoint = int(tracking_file.read())
  # print last_checkpoint
  if(current_checkpoint - last_checkpoint > step):
    renew()
    tracking_file.close()

def renew():
  t = Taskr()
  t.renewTaskAt(last_checkpoint)
  t.saveTasks()
  sys.exit(0)

o = open_file()
while(alive):
  write_time(o)
  time.sleep(step)
  current_checkpoint = int(time.time())
  read_time(o)
# os.rename(path + wsid + ".ttmp",path + wsid + ".DEL")
