#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main import db
from datetime import datetime


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    openid = db.Column(db.String(32), unique=True, nullable=False)
    nickname = db.Column(db.String(32), nullable=True)
    realname = db.Column(db.String(10), nullable=True)
    classname = db.Column(db.String(10), nullable=True)
    sex = db.Column(db.SmallInteger, default=0, nullable=False)
    province = db.Column(db.String(10), nullable=True)
    city = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(20), nullable=True)
    headimgurl = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(32), nullable=True)
    regtime = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, openid, nickname=None, realname=None,
                 classname=None, sex=None, province=None, city=None,
                 country=None, headimgurl=None, email=None, regtime=None):
        self.openid = openid
        self.nickname = nickname
        self.realname = realname
        self.classname = classname
        self.sex = sex
        self.province = province
        self.city = city
        self.country = country
        self.headimgurl = headimgurl
        self.email = email
        self.regtime = regtime

    def __repr__(self):
        return '<openid %r>' % self.openid


class Sign(db.Model):

    openid = db.Column(db.String(32), primary_key=True, unique=True,
                       nullable=False)
    lastsigntime = db.Column(db.BigInteger, default=0, nullable=False)
    totaldays = db.Column(db.SmallInteger, default=0, nullable=False)
    keepdays = db.Column(db.SmallInteger, default=0, nullable=False)

    def __init__(self, openid, lastsigntime, totaldays, keepdays):
        self.openid = openid
        self.lastsigntime = lastsigntime
        self.totaldays = totaldays
        self.keepdays = keepdays

    def __repr__(self):
        return '<openid %r>' % self.openid


class Express(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    openid = db.Column(db.String(32), nullable=False)
    num = db.Column(db.String(20), nullable=False)
    comcode = db.Column(db.String(10), nullable=False)
    lastupdate = db.Column(db.DateTime, nullable=True)

    def __init__(self, openid, num, comcode, lastupdate):
        self.openid = openid
        self.num = num
        self.comcode = comcode
        self.lastupdate = lastupdate

    def __repr__(self):
        return '<id %r>' % self.id


class Auth(db.Model):

    openid = db.Column(db.String(32), primary_key=True, unique=True,
                       nullable=False)
    studentid = db.Column(db.String(20), nullable=True)
    studenidpwd = db.Column(db.String(40), nullable=True)
    libraryid = db.Column(db.String(20), nullable=True)
    libraryidpwd = db.Column(db.String(40), nullable=True)

    def __init__(self, openid, studentid, studenidpwd, libraryid,
                 libraryidpwd):
        self.openid = openid
        self.studentid = studentid
        self.studenidpwd = studenidpwd
        self.libraryid = libraryid
        self.libraryidpwd = libraryidpwd

    def __repr__(self):
        return '<openid %r>' % self.openid
