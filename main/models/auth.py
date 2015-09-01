#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import db


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
