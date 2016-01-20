#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import db


class Sign(db.Model):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }

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

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def update(self):
        db.session.commit()
        return self
