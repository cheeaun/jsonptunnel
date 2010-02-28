#!/usr/bin/env python

import re
import cgi
import urllib
import logging
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.api import urlfetch

class MainHandler(webapp.RequestHandler):
  def get(self):
    extURL = cgi.escape(self.request.get('extURL'))
    extMethod = cgi.escape(self.request.get('extMethod'))
    queryString = cgi.escape(self.request.query_string)
    queryDict = dict(cgi.parse_qsl(queryString)) 
    callback = cgi.escape(self.request.get('_callback'))
    
    if queryString:
      error = 1
      method = urlfetch.POST
      
      if extURL: del queryDict['extURL']
      if extMethod:
        del queryDict['extMethod']
        m = extMethod.lower()
        if m == 'put': method = urlfetch.PUT
        elif m == 'delete': method = urlfetch.DELETE
        elif m == 'get': method = urlfetch.GET # Huh??
        elif m == 'head': method = urlfetch.HEAD # Oh, wait the minute...
      
      if len(queryDict):
        try:
          data = urllib.urlencode(queryDict)
          result = urlfetch.fetch(extURL, method=method, payload=data)
          if result.status_code == 200 or result.status_code == 201:
            error = 0
            self.response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
            content = result.content
            if callback:
              logging.info('Adding callback to JSON')
              exp = re.compile('^[A-Za-z_$][A-Za-z0-9._$]*?$')
              match = exp.match(callback)
              if match: content = callback + '(' + content.decode('utf-8') + ')'
            self.response.out.write(content)
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
      <style>
      body{font-family: helvetica, arial, sans-serif}
      var{font-weight: bold; font-style: normal;}
      dt{display: list-item;}
      dl{margin-left: 40px;}
      </style>
      <h1>jsonptunnel</h1>
      <p>JSONP tunnel for letting you POST to remote services from your client-side JavaScript application and receive JSONP data.</p>
      <p><a href="http://labs.thinkminimo.com/jsonptunnel/#example">Try it out on the example form</a> and put <strong>http://jsonptunnel.appspot.com/</strong> as the jsonptunnel URL.</p>
      <p>Or try the following URL: <a href="/?callback=foo&amp;extURL=http://dipert.org/alan/calc.php&amp;num1=1&amp;num2=2">/?callback=foo&amp;extURL=http://dipert.org/alan/calc.php&amp;num1=1&amp;num2=2</a></p>
      <p>The parameters:</p>
      <dl>
      <dt><var>extURL</var></dt>
        <dd>Indicates the <em>external</em> web service URL. <strong>Required</strong>.</dd>
      <dt><var>extMethod</var> <em>(experimental)</em></dt>
        <dd>Indicates the HTTP method to use for the request, such as:
          <ul>
          <li>post <em>(default)</em></li>
          <li>put</li>
          <li>delete</li>
          </ul>
        </dd>
      <dt>...and any parameters to pass to the web service.</dt>
      </dl>
      <p>Inspired by <a href="http://ubergibson.com/">Alan Dipert</a>'s <a href="http://labs.thinkminimo.com/jsonptunnel/">jsonptunnel</a>. <a href="http://jsonptunnel.googlecode.com/">Google Code</a></p>
      """)

def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
