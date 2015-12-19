#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Peng Ding @ 2015-12-17 14:37:25

from google.appengine.ext import ndb
import datetime

class Tag(ndb.Model):
    tag_name = ndb.StringProperty()
    total_res = ndb.IntegerProperty(default=0)


class Resource(ndb.Model):
    name = ndb.StringProperty()
    owner = ndb.UserProperty()
    start_time = ndb.DateTimeProperty()
    end_time = ndb.DateTimeProperty()
    tags = ndb.StructuredProperty(Tag, repeated=True)
    last_res_time = ndb.DateTimeProperty(default=None)
    description = ndb.StringProperty(default="")
    reserved_num = ndb.IntegerProperty(default=0)
    capacity = ndb.IntegerProperty(default=1)
    image = ndb.BlobProperty()


class Reservation(ndb.Model):
    start = ndb.DateTimeProperty()
    end = ndb.DateTimeProperty()
    reserver = ndb.UserProperty()
    reserve_time = ndb.DateTimeProperty(auto_now_add=True)


def AllResource():
    return Resource.query().order(-Resource.last_res_time)


def FilterResourceByName(resources, name):
    # naive implementation, just compare string
    results = []
    for res in resources:
        if name in res.name:
            results.append(res)
    return results


def GetResourceByDatetime(start, end):
    resources = AllResource()
    results = []
    for c_res in resources:
        reservations = GetResourceReservation(c_res)
        cur_reserve_num = 0
        for res in reservations:
            if (start <= res.start and end >= res.start) or (start <= res.end and end >= res.end):
                    cur_reserve_num += 1
        if cur_reserve_num < c_res.capacity and c_res.start_time.time() < start.time() and c_res.end_time.time() > end.time():
            results.append(c_res)
    return results


def MyResource(user):
    return Resource.query(Resource.owner==user)


def GetResource(id):
    return Resource.get_by_id(id)


def GetReservation(id, parent):
    return Reservation.get_by_id(id, parent=parent.key)


def AllReservations(user):
    return Reservation.query(Reservation.reserver==user).order(Reservation.reserve_time)


def AllUsersReservations():
    return Reservation.query()


def GetResourceReservation(resource):
    return Reservation.query(ancestor=resource.key).order(Reservation.reserve_time)


def AllTags():
    return Tag.query()


def GetTag(id):
    return Tag.get_by_id(id)


def GetTagbyName(name):
    return Tag.query(Tag.tag_name==name).get()


def GetTagResource(tag):
    return Resource.query(Resource.tags==tag)


def AddResource(user, name, start_time, end_time,
                tags, capacity, description):
    res = Resource(name=name, owner=user, start_time=start_time,
                   end_time=end_time, capacity=capacity, tags=tags,
                   description=description)
    res.put()
    for t in tags:
        tag = GetTagbyName(t.tag_name)
        tag.total_res += 1
        tag.put()
    return res


def AddReservation(user, resource, start, end):
    reservation = Reservation(reserver=user, start=start, end=end, parent=resource.key)
    reservation.put()
    resource.last_res_time = datetime.datetime.now()
    resource.reserved_num += 1
    resource.put()
    return reservation


def AddTag(name):
    if not Tag.query(Tag.tag_name==name).get():
        tag = Tag(tag_name=name)
        tag.put()
        return tag
    else:
        return Tag.query(Tag.tag_name==name).get()


def DelReservation(id, parent):
    key = ndb.Key(Reservation, id, parent=parent.key)
    key.delete()


def UpdateResource(id, owner, name, start_time, end_time,
                   tags, capacity, description):
    res = id.get()
    res.owner = owner
    res.name = name
    res.start_time = start_time
    res.end_time = end_time
    res.tags = tags
    res.capacity = capacity
    res.description = description
    res.put()
    return res
