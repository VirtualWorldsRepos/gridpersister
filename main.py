#!/usr/bin/env python
#$Id: main.py 4 2009-09-06 17:57:10Z lkalif $

import service
import webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from uuid import uuid4


class UrlHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(
          template.render('templates/main.html', {}))

class AboutUrlHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(
          template.render('templates/about.html', {}))
        
class RandomNiceUrlHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(
          template.render('templates/random_nice.html', { "uuid" : uuid4() }))

class RandomUrlHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers["Content-type"] = "text/plain"
        self.response.out.write(uuid4())

app = webapp2.WSGIApplication([
      ('/', UrlHandler),
      ('/random', RandomNiceUrlHandler),
      ('/rand', RandomUrlHandler),
      ('/about', AboutUrlHandler),
      ('/reg', service.RegistrationHandler),
      ('/go/.*', service.GoHandler),
      ('/get/.*', service.FetchHandler),
      ], debug=True)
