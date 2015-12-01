#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import db


class Auth(db.Model):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    openid = db.Column(db.String(32), primary_key=True, unique=True,
                       nullable=False)
    studentid = db.Column(db.String(20), nullable=True)
    studentpwd = db.Column(db.String(100), nullable=True)
    libraryid = db.Column(db.String(20), nullable=True)
    librarypwd = db.Column(db.String(100), nullable=True)

    def __init__(self, openid, studentid, studentpwd, libraryid,
                 librarypwd):
        self.openid = openid
        self.studentid = studentid
        self.studentpwd = studentpwd
        self.libraryid = libraryid
        self.librarypwd = librarypwd

    def __repr__(self):
        return '<openid %r>' % self.openid

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def update(self):
        db.session.commit()
        return self
