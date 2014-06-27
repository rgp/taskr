def open_html():
  html = '''<!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="">
        <meta name="author" content="">
  '''
def title(title="Untitled"):
  return "<title>"+title+"</title>"
def html_assets():

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
