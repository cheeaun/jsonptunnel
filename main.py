#!/usr/bin/env python

import cgi
import urllib
import logging
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.api import urlfetch

class MainHandler(webapp.RequestHandler):
  def get(self):
    extURL = cgi.escape(self.request.get('extURL'))
    queryString = cgi.escape(self.request.query_string)
    queryDict = dict(cgi.parse_qsl(queryString)) 
    
    if queryString:
      error = 1
      if extURL:
        del queryDict['extURL']
        
        if len(queryDict):
          try:
            data = urllib.urlencode(queryDict)
            result = urlfetch.fetch(extURL, method='POST', payload=data)
            if result.status_code == 200:
              error = 0
              self.response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
              self.response.out.write(result.content)
          except urlfetch.Error:
            logging.error('urlfetch error')
            error = 1
     
      if error:
        self.response.set_status(400)
        self.response.out.write('Status: 400 Error parsing URL. There was an error processing your request: Error parsing URL.')
      
    else:
      self.response.out.write("""
      <!DOCTYPE html>
      <title>jsonptunnel</title>
      <h1>jsonptunnel</h1>
      <p>JSONP tunnel for letting you POST to remote services from your client-side JavaScript application and receive JSONP data.</p>
      <p><a href="http://labs.thinkminimo.com/jsonptunnel/#example">Try it out on the example form</a> and put <strong>http://jsonptunnel.appspot.com/</strong> as the jsonptunnel URL.</p>
      <p>Or the following URL: <a href="/?callback=foo&amp;extURL=http://dipert.org/alan/calc.php&amp;num1=1&amp;num2=2">/?callback=foo&amp;extURL=http://dipert.org/alan/calc.php&amp;num1=1&amp;num2=2</a></p>
      <p>Inspired by <a href="http://ubergibson.com/">Alan Dipert</a>'s <a href="http://labs.thinkminimo.com/jsonptunnel/">jsonptunnel</a>. <a href="http://jsonptunnel.googlecode.com/">Google Code</a></p>
      """)

def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
