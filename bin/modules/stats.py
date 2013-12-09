import time
import BaseHTTPServer
from os.path import expanduser
from math import ceil
t = __import__("taskr")


HOST_NAME = '' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8080 # Maybe set this to 9000.

def read_assets():
  home = expanduser("~") + "/"
  dir = home + ".taskr/"
  with open(dir + '_gsapi.js', 'r') as content_file:
    gsapi = content_file.read()
  with open(dir + 'chartkick.js', 'r') as content_file:
    chartkick = content_file.read()
  with open(dir + 'bootstrap.min.css', 'r') as content_file:
    bootstrap = content_file.read()
  with open(dir + 'goog.js', 'r') as content_file:
    goog = content_file.read()
  return gsapi,chartkick,bootstrap,goog

def html_head(s):
  s.wfile.write('''<!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="">
        <meta name="author" content="">
  ''')
  s.wfile.write("<title>Taskr statistics</title>")
  g,c,b,go = read_assets()
  s.wfile.write('<script type="text/javascript">')
  s.wfile.write(g)
  s.wfile.write('</script>')
  s.wfile.write('<style>')
  s.wfile.write(b)
  s.wfile.write('</style>')
  s.wfile.write('<script type="text/javascript">')
  s.wfile.write(c)
  s.wfile.write('</script>')
  s.wfile.write('<script type="text/javascript">')
  s.wfile.write(go)
  s.wfile.write('</script>')
  s.wfile.write("</head>")
  s.wfile.write("<body>")
  html_body(s)
  s.wfile.write("</body></html>")

def html_body(s):
  s.wfile.write("<div class='container'>")
  s.wfile.write("<h1>My statistics</h1>")
  if s.path == "/":
    menu(s)
  else:
    timeline(s)

def menu(s):
  taskr = t.Taskr()
  tasks = taskr.tasks
  tasks = [{k: v for k, v in d.iteritems() if k == 'elapsed' or k == 'id' or k == 'name' or k == 'status'} for d in tasks]
  s.wfile.write("<table>")
  for task in tasks:
    s.wfile.write("<tr>")
    s.wfile.write("<td>")
    s.wfile.write(task["name"])
    s.wfile.write("</td>")
    s.wfile.write("<td>")
    s.wfile.write(humanTime(task["elapsed"]))
    s.wfile.write("</td>")
    s.wfile.write("<td>")
    s.wfile.write("<a href='/"+str(task["id"])[0:8]+"'> View details</a>")
    s.wfile.write("</td>")
    s.wfile.write("</tr>")
  s.wfile.write("</table>")

def show():
  pass

def timeline(s):
  taskr = t.Taskr()
  try:
    task = taskr._Taskr__findtask(s.path[1:])
    s.wfile.write("<h3>"+task["name"]+"</h3>")
    l = len(task["worklog"])
    render = '<div id="example1" style="width: 900px; height: '+str(l*38+100)+'px;"></div>'
    render +=  """
    <script type="text/javascript">
  google.setOnLoadCallback(drawChart);

  function drawChart() {
    var container = document.getElementById('example1');
    a = container;

    var chart = new google.visualization.Timeline(container);

    var dataTable = new google.visualization.DataTable();

    dataTable.addColumn({ type: 'string', id: 'Session' });
    dataTable.addColumn({ type: 'date', id: 'Start' });
    dataTable.addColumn({ type: 'date', id: 'End' });

    dataTable.addRows([ """
    i = 1
    for w in sorted(task["worklog"]):
      log = task["worklog"][w]
      h,m = hoursmins(log["duration"])
      render += "[ 'Session "+str(i)+"', new Date("+str(w)+"*1000), "+ ("new Date("+str(w+log["duration"]*3600)+"*1000)" if log["duration"] != 0 else "new Date()") +" ]"
      render += "," if i < l else ""
      i += 1
    render += "]);"
    render += """
    chart.draw(dataTable);
  }
  </script>
  """
    s.wfile.write(render)
  except Exception:
    s.wfile.write("Task not found")

def load_tasks():
  return t.Taskr().tasks

def hoursmins(time):
  dec = (time - int(time))
  minutes = roundup(dec*60,0)
  hours = roundup(time - dec,2)
  return int(hours),int(minutes)

def humanTime(time):
  dec = (time - int(time))
  minutes = roundup(dec*60,0)
  hours = roundup(time - dec,2)
  return str(int(hours))+"h "+str(int(minutes))+"m"

def roundup(number,decimals):
    val = pow(10,decimals)
    return ceil(number * val) / val


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  def do_HEAD(s):
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()

  def do_GET(s):
    """Respond to a GET request."""
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()

    html_head(s)
    

  def log_message(self, format, *args):
    # open(LOGFILE, "a").write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format%args))
    pass

  def log_error(self,*args):
    return BaseHTTPServer.BaseHTTPRequestHandler.log_error(self,*args)




if __name__ == '__main__':
  server_class = BaseHTTPServer.HTTPServer
  httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
  print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
  try:
      httpd.serve_forever()
  except KeyboardInterrupt:
      pass
  httpd.server_close()
  print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
