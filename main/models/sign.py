#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import db


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
