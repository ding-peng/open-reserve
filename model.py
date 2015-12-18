#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Peng Ding @ 2015-12-17 14:37:25

from google.appengine.ext import ndb
import datetime

class Tag(ndb.Model):
    tag_name = ndb.StringProperty()


class Resource(ndb.Model):
    name = ndb.StringProperty()
    owner = ndb.UserProperty()
    start_time = ndb.IntegerProperty()
    end_time = ndb.IntegerProperty()
    tags = ndb.StructuredProperty(Tag, repeated=True)
    last_res_time = ndb.DateTimeProperty(default=None)
    description = ndb.StringProperty(default="")
    reserved_num = ndb.IntegerProperty(default=0)
    capacity = ndb.IntegerProperty(default=1)


class Reservation(ndb.Model):
    resource = ndb.StructuredProperty(Resource)
    start = ndb.DateTimeProperty()
    end = ndb.DateTimeProperty()
    # TODO: add validator
    reserver = ndb.UserProperty()
    reserve_time = ndb.DateTimeProperty(auto_now_add=True)


def AllResource():
    return Resource.query().order(-Resource.last_res_time)


def MyResource(user):
    return Resource.query(Resource.owner==user)


def GetResource(id):
    return Resource.query(id=id)


def AllReservations(user):
    # TODO: time has passed
    return Reservation.query(Reservation.reserver==user).order(Reservation.reserve_time)


def GetResourceReservation(resource):
    return Reservation.query(resource==resource).order(Reservation.reserve_time)

def AllTags():
    return Tag.query()


def AddResource(user, name, start_time, end_time,
                tags, capacity, description):
    res = Resource(name=name, owner=user, start_time=start_time,
                   end_time=end_time, capacity=capacity, tags=tags,
                   description=description)
    res.put()
    return res


def AddReservation(user, resource, start, end):
    reservation = Reservation(resource=resource,
                              owner=user, start=start, end=end)
    reservation.put()
    resource.last_res_time = datetime.datetime.now()
    resource.reserved_num += 1
    resource.put()
    return reservation


def AddTag(name):
    tag = Tag(name)
    tag.put()
    return Tag


def DelReservation(id):
    key = ndb.Key(Reservation, id)
    key.delete()


def UpdateResource(id, name, start_time, end_time,
                   tags, capacity, description):
    res = Resource(id=id, name=name, start_time=start_time,
                   end_time=end_time, capacity=capacity, tags=tags,
                   description=description)
    res.put()
    return res
