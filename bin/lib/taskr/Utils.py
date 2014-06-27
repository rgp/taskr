from math import ceil
from termcolor import colored
import datetime

class Utils():

  readableStatus = {
      0:colored("Closed","cyan"),
      1:colored("Active","green"),
      2:colored("Paused","yellow",None,["blink"]),
      3:colored("Pending","magenta")}

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
