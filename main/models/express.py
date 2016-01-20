#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import db


class Express(db.Model):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    openid = db.Column(db.String(32), primary_key=True, nullable=False)
    num = db.Column(db.String(30), primary_key=True, nullable=False)
    comcode = db.Column(db.String(20), nullable=False)
    lastupdate = db.Column(db.String(25), nullable=False)
    ischeck = db.Column(db.SmallInteger, default=0, nullable=False)

    def __init__(self, openid, num, comcode, lastupdate, ischeck):
        self.openid = openid
        self.num = num
        self.comcode = comcode
        self.lastupdate = lastupdate
        self.ischeck = ischeck

    def __repr__(self):
        return '<id %r>' % self.id

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def update(self):
        db.session.commit()
        return self
