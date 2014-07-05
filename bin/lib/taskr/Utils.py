import datetime
from math import ceil
from termcolor import colored
from prettytable import PrettyTable

class Utils():

  tags = {}

  readableStatus = {
      0:colored("Closed","cyan"),
      1:colored("Active","green"),
      2:colored("Paused","yellow",None,["blink"]),
      3:colored("Pending","magenta")}

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

  @staticmethod
  def datefmt(time):
    return datetime.datetime.fromtimestamp(time).strftime('%y-%m-%d %H:%M')

  @staticmethod
  def roundup(number,decimals):
    val = pow(10,decimals)
    return ceil(number * val) / val

  @staticmethod
  def hourstohuman(time):
    dec = (time - int(time))
    minutes = Utils.roundup(dec*60,0)
    hours = Utils.roundup(time - dec,2)
    return str(int(hours))+"h "+str(int(minutes))+"m"

  @staticmethod
  def colorTags(tag):
    if tag not in Utils.tags:
      cindex = len(Utils.tags) % 8
      Utils.tags[tag] = colored(tag,Utils.colors[cindex])
    return Utils.tags[tag]

  @staticmethod
  def tableHeader(detailed=False):
    if detailed:
      return PrettyTable(["ID","Task","Tag","Estimated","Sessions","Last Worked On","Curr session","Total time","Status"])
    return PrettyTable(["ID","Task","Tag","Last Worked On","Curr session","Total time","Status"])

  @staticmethod
  def workSessionsTableHeader():
    return PrettyTable(["","Start","End","Duration","Working Directory"])
