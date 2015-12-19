#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Peng Ding @ 2015-12-17 20:30:00


import os
import urllib
import cgi
import jinja2
import webapp2
from datetime import datetime, date, time

from google.appengine.api import users
from google.appengine.api import images
from google.appengine.api import mail
from google.appengine.ext import ndb

import model

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+'/templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Resource(webapp2.RequestHandler):

    def get(self, resource_id):
        user = users.get_current_user()
        if user:
            log_url = users.create_logout_url(self.request.uri)
            resource = model.GetResource(int(resource_id))
            reservations = model.GetResourceReservation(resource)
            values = {'resource': resource,
                      'reservations': reservations,
                      'user': user,
                      'now': datetime.now(),
                      'log_url': log_url}
            template = JINJA_ENVIRONMENT.get_template('resource.html')
            self.response.write(template.render(values))
        else:
            log_url = users.create_login_url(self.request.uri)
            self.redirect(users.create_login_url(self.request.uri))


    def post(self, resource_id):
        user = users.get_current_user()
        if user:
            try:
                resource = model.GetResource(int(resource_id))
                if resource.owner == user:
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
                    new_resource = model.UpdateResource(resource.key,
                                                        user, name, start_time, end_time,
                                                        tags, capacity, description)
                    image = self.request.get('img')
                    if image:
                        image = images.resize(image, 200, 200)
                        resource.image = image
                        resource.put()
                    self.redirect("/resource/"+resource_id)
            except Exception as e:
                print e
                self.redirect("/resource/"+resource_id)
        else:
            log_url = users.create_login_url(self.request.uri)
            self.redirect(users.create_login_url(self.request.uri))

class Reserve(webapp2.RequestHandler):

    def post(self, resource_id):
        user = users.get_current_user()
        if user:
            try:
                resource = model.GetResource(int(resource_id))
                date = cgi.escape(self.request.get('date'))
                date = datetime.strptime(date, "%Y-%m-%d")
                start = cgi.escape(self.request.get('start'))
                end = cgi.escape(self.request.get('end'))
                start_time = datetime.strptime(start, "%H:%M").time()
                end_time = datetime.strptime(end, "%H:%M").time()
                start_datetime = datetime.combine(date, start_time)
                end_datetime = datetime.combine(date, end_time)
                if (start_time <= resource.start_time.time() and end_time >= resource.start_time.time()) or (start_time <= resource.end_time.time() and end_time >= resource.end_time.time()):
                    self.redirect("/")
                current_res = model.GetResourceReservation(resource)
                cur_reserve_num = 0
                for res in current_res:
                    if (start_datetime <= res.start and end_datetime >= res.start) or (start_datetime <= res.end and end_datetime >= res.end):
                        cur_reserve_num += 1
                user_has_no_res = True
                user_reservations = model.AllReservations(user)
                for u_res in user_reservations:
                    if (start_datetime <= u_res.start and end_datetime >= u_res.start) or (start <= u_res.end and end_datetime >= u_res.end):
                        user_has_no_res = False
                if cur_reserve_num < resource.capacity and user_has_no_res and end_time > start_time:
                    resveration = model.AddReservation(user, resource, start_datetime,
                                                    end_datetime)
                else:
                    pass
                self.redirect("/resource/"+resource_id)
            except Exception as e:
                print e
                self.redirect("/resource/"+resource_id)
        else:
            log_url = users.create_login_url(self.request.uri)
            self.redirect(users.create_login_url(self.request.uri))


class Tag(webapp2.RequestHandler):

    def get(self, tag_id):
        user = users.get_current_user()
        if user:
            log_url = users.create_logout_url(self.request.uri)
            tag = model.GetTagbyName(tag_id)
            if not tag:
                tag = model.GetTag(int(tag_id))
            resources = model.GetTagResource(tag)
            print tag, resources
            values = {'tag': tag,
                    'resources': resources,
                    'log_url': log_url}
            template = JINJA_ENVIRONMENT.get_template('tag.html')
            self.response.write(template.render(values))
        else:
            log_url = users.create_login_url(self.request.uri)
            self.redirect(users.create_login_url(self.request.uri))


class Search(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            log_url = users.create_logout_url(self.request.uri)
            text = cgi.escape(self.request.get('name')).strip()
            date = cgi.escape(self.request.get('date'))
            start = cgi.escape(self.request.get('search_start'))
            end = cgi.escape(self.request.get('search_end'))
            time_limit = False
            if date and start and end:
                date = datetime.strptime(date, "%Y-%m-%d")
                start_time = datetime.strptime(start, "%H:%M").time()
                end_time = datetime.strptime(end, "%H:%M").time()
                start_datetime = datetime.combine(date, start_time)
                end_datetime = datetime.combine(date, end_time)
                resources = model.GetResourceByDatetime(start_datetime, end_datetime)
                resources = model.FilterResourceByName(resources, text)
                time_limit = True
            else:
                resources = model.FilterResourceByName(model.AllResource(), text)
            values = {"search": text,
                      "resources": resources,
                      "limit": time_limit,
                      "date": date,
                      "start": start,
                      "end": end,
                      'log_url': log_url}
            template = JINJA_ENVIRONMENT.get_template('tag.html')
            self.response.write(template.render(values))
        else:
            log_url = users.create_login_url(self.request.uri)
            self.redirect(users.create_login_url(self.request.uri))


class Rss(webapp2.RequestHandler):

    def get(self, resource_id):
        resource = model.GetResource(int(resource_id))
        if resource:
            self.response.content_type = "text/xml"
            self.response.write('<?xml version="1.0" encoding="UTF-8" ?>')
            self.response.write('<rss version="2.0">')
            self.response.write('<channel>')
            self.response.write('<title>' + resource.name + '</title>')
            if resource.description:
                self.response.write('<description>' + resource.description + '</description>')
            else:
                self.response.write('<description>' + resource.name + '</description>')
            self.response.write('<link>' + self.request.url.replace("/rss","") + '</link>')
            self.response.write('<lastBuildDate>' + datetime.now().strftime("%b, %d %Y %H:%M") + '</lastBuildDate>')
            self.response.write('<pubDate>' + datetime.now().strftime("%b, %d %Y %H:%M") + '</pubDate>')
            self.response.write('<ttl>1800</ttl>')
            reservations = model.GetResourceReservation(resource)
            for res in reservations:
                self.response.write('<item>')
                self.response.write('<reserver>' + res.reserver + '</reserver>')
                self.response.write('<reserveDate>' + res.reserve_time + '</reserveDate>')
                self.response.write('<start>' + res.start + '</start>')
                self.response.write('<end>' + res.end + '</end>')
                self.response.write('</item>')
            self.response.write('</channel>')
            self.response.write('</rss>')


class Image(webapp2.RequestHandler):

    def get(self):
        resource = ndb.Key(urlsafe=self.request.get('img_id')).get()
        if resource.image:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(resource.image)
        else:
            self.response.out.write('No image')


class Main(webapp2.RequestHandler):

    def get(self):
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/resource/(\d+)', Resource),
    ('/resource/search', Search),
    ('/resource/edit/(\d+)', Resource),
    ('/resource/rss/(\d+)', Rss),
    ('/resource/reserve/(\d+)', Reserve),
    ('/resource/tag/(\w+)', Tag),
    ('/resource/img', Image),
    ('/resource/.*', Main),
], debug=True)
