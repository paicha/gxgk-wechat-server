#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import db


class Express(db.Model):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = db.Column(db.Integer, autoincrement=True)
    openid = db.Column(db.String(32), primary_key=True, nullable=False)
    num = db.Column(db.String(20), primary_key=True, nullable=False)
    comcode = db.Column(db.String(10), nullable=False)
    lastupdate = db.Column(db.DateTime, nullable=True)
    ischeck = db.Column(db.SmallInteger, default=0, nullable=False)

    def __init__(self, openid, num, comcode, lastupdate):
        self.openid = openid
        self.num = num
        self.comcode = comcode
        self.lastupdate = lastupdate

    def __repr__(self):
        return '<id %r>' % self.id
