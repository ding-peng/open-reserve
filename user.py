#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Peng Ding @ 2015-12-18 13:01:07



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


class User(webapp2.RequestHandler):

    def get(self, user_id):
        user = users.User(_user_id = user_id)
        if user:
            reservations = model.AllReservations(user)
            resources = model.AllResource()
            values = {'resources': resources,
                      'reservations': reservations}
            template = JINJA_ENVIRONMENT.get_template('user.html')
            self.response.write(template.render(values))
        else:
            log_url = users.create_login_url(self.request.uri)
            self.redirect(users.create_login_url(self.request.uri))


class Deletion(webapp2.RequestHandler):

    def get(self, resource_id, reservation_id):
        user = users.get_current_user()
        if user:
            resource = model.GetResource(int(resource_id))
            reservation = model.GetReservation(int(reservation_id), resource)
            if reservation.reserver == user:
                model.DelReservation(int(reservation_id), resource)
            self.redirect('/')
        else:
            pass


app = webapp2.WSGIApplication([
    ('/user/(\d+)', User),
    ('/user/del/(\d+)/(\d+)', Deletion),
], debug=True)
