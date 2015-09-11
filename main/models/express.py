#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import db


class Express(db.Model):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

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
