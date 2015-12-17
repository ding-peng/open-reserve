#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Peng Ding @ 2015-12-17 16:08:43


import os
import urllib
import jinja2
import webapp2

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
            values = {'resources':resources,
                      'reservations': reservations}
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(values))
        else:
            log_url = users.create_login_url(self.request.uri)
            self.redirect(users.create_login_url(self.request.uri))


app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
