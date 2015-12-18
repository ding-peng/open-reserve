#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Peng Ding @ 2015-12-17 16:08:43


import os
import urllib
import cgi
import jinja2
import webapp2
from datetime import datetime, date, time

from google.appengine.api import users

import model

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+'/templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            log_url = users.create_logout_url(self.request.uri)
            reservations = model.AllReservations(user)
            resources = model.AllResource()
            tags = model.AllTags()
            my_resources = model.MyResource(user)
            values = {'resources':resources,
                      'reservations': reservations,
                      'tags': tags,
                      'my_resources': my_resources}
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(values))
        else:
            log_url = users.create_login_url(self.request.uri)
            self.redirect(users.create_login_url(self.request.uri))
         

class Resource(webapp2.RequestHandler):
    
    def post(self):
        user = users.get_current_user()
        if user:
            try:
                name = cgi.escape(self.request.get('resourceName'))
                owner = user
                start = cgi.escape(self.request.get('start'))
                end = cgi.escape(self.request.get('end'))
                start_time = datetime.strptime(start, "%H:%M")
                end_time = datetime.strptime(end, "%H:%M")
                if start_time > end_time:
                    self.redirect("/")
                tags = []#cgi.escape(self.request.get('tags'))
                capacity = int(cgi.escape(self.request.get('capacity')))
                description = cgi.escape(self.request.get('description'))
                resource = model.AddResource(user, name, start_time, end_time,
                                             tags, capacity, description)
                self.redirect("/")
            except:
                self.redirect("/")
            # TODO: change to resource page

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/add', Resource),
], debug=True)
