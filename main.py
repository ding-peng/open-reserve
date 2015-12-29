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
from google.appengine.api import images
from google.appengine.api import mail

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
            my_resources = model.MyResource(user)
            values = {'resources': resources,
                      'reservations': reservations,
                      'my_resources': my_resources,
                      'log_url': log_url}
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(values))
        else:
            log_url = users.create_login_url(self.request.uri)
            self.redirect(users.create_login_url(self.request.uri))


class Resource(webapp2.RequestHandler):

    def get(self):
        self.redirect("/")

    def post(self):
        user = users.get_current_user()
        if user:
            try:
                name = cgi.escape(self.request.get('resourceName')).strip()
                owner = user
                start = cgi.escape(self.request.get('start')).strip()
                end = cgi.escape(self.request.get('end')).strip()
                start_time = datetime.strptime(start, "%H:%M")
                end_time = datetime.strptime(end, "%H:%M")
                if start_time > end_time:
                    self.redirect("/")
                raw_tags = cgi.escape(self.request.get('tags')).strip().split(" ")
                tags = []
                for t in raw_tags:
                    tags.append(model.AddTag(t))
                capacity = int(cgi.escape(self.request.get('capacity')).strip())
                description = cgi.escape(self.request.get('des')).strip()
                resource = model.AddResource(user, name, start_time, end_time,
                                             tags, capacity, description)
                image = self.request.get('img')
                if image:
                    image = images.resize(image, 200, 200)
                    resource.image = image
                    resource.put()
                self.redirect("/")
            except Exception as e:
                print e
                self.redirect("/")
        else:
            log_url = users.create_login_url(self.request.uri)
            self.redirect(users.create_login_url(self.request.uri))


class Cron(webapp2.RequestHandler):

    def get(self):
        reservations = model.AllUsersReservations()
        for res in reservations:
            if res.end <= datetime.now():
                model.DelReservation(res.key.id(), res.key.parent().get())
            if res.start >= datetime.now():
                try:
                    mail_body = ("You've reservation " + resource.name +
                                 " has started!")
                    mail.send_mail(sende="Open Reserve <support@openreserve.com>",
                                   to='<' + res.reserver.email + '>',
                                   subject="Reservation Start",
                                   body=mail_body)
                except:
                    pass


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/add', Resource),
    ('/check', Cron),
], debug=True)
