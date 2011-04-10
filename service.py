#!/usr/bin/env python

import wsgiref.handlers
import uuid
import string
import logging
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from urlparse import urlparse
from google.appengine.api import memcache

class GridUrl(db.Model):
    service = db.StringProperty(required = True)
    url = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    updated = db.DateTimeProperty(auto_now = True)
    
    def save(self):
        self.put()
        memcache.set(self.service, str(self.url))
      
    @staticmethod
    def load(service, only_cache = False):
        url = memcache.get(service)
        if (url is None) and (not only_cache):
            url = GridUrl.get_by_key_name("service_%s" % str(service))
            if url is not None:
                url = str(url.url)
                memcache.set(service, url)
                return url
            else:
                return none
        elif url is not None:
            return url
        else:
            return None
 
class RegistrationHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers["Content-type"] = "text/plain"
        try:
            service = uuid.UUID("{" + self.request.get("service") + "}")
            url = urlparse(self.request.get("url"))
            if url.scheme != "http" and url.scheme != "https":
                raise Exception("Only http and https urls supported for url= parameter")
            url = self.request.get("url")
            key = "service_%s" % str(service)
            gridUrl = GridUrl(key_name = key, service = str(service), url = url)
            gridUrl.save()
            self.response.out.write("OK");
        except Exception, ex:
            self.response.set_status(503)
            self.response.out.write("ERROR^" + str(ex.message));
            return

class GoHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers["Content-type"] = "text/plain"
        try:
            url = GridUrl.load(self.request.path.split("/")[2])
            if url is None:
                raise Exception("Service not found")

            if self.request.query != "":
                url += "?" + self.request.query

            self.response.set_status(302)
            self.response.headers["Location"] = url
            self.response.out.write(url)
        except Exception, ex:
            self.response.set_status(404)
            self.response.out.write("ERROR^" + str(ex.message));
            return
        
    def post(self):
        try:
            url = GridUrl.load(self.request.path.split("/")[2])
            if url is None:
                raise Exception("Service not found")
            
            if self.request.query != "":
                url += "?" + self.request.query
            
            content_type = self.request.headers.get("Content-Type", "application/x-www-form-urlencoded")

            res = urlfetch.fetch(url = url,
                                 method = urlfetch.POST,
                                 payload = self.request.body,
                                 headers = {"Content-Type": content_type}
            )

            self.response.headers["content-type"] = res.headers["content-type"]

            for h in res.headers:
                if h.find("x-secondlife") == 0:
                    self.response.headers[h] = res.headers[h]
            
            self.response.set_status(res.status_code)
            self.response.out.write(res.content)
        except Exception, ex:
            self.response.headers["Content-type"] = "text/plain"
            self.response.set_status(404)
            self.response.out.write("ERROR^" + str(ex.message));
            return
        

class FetchHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers["Content-type"] = "text/plain"
        try:
            gridUrl = GridUrl.load(self.request.path.split("/")[2])
            if gridUrl is None:
                raise Exception("Service not found")
            self.response.out.write(gridUrl)
        except Exception, ex:
            self.response.set_status(404)
            self.response.out.write("ERROR^" + str(ex.message));
            return
