#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import db
from . import redis
from datetime import datetime

redis_prefix = "wechat:user:"


class User(db.Model):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    openid = db.Column(db.String(32), unique=True, nullable=False)
    nickname = db.Column(db.String(32), nullable=True)
    realname = db.Column(db.String(10), nullable=True)
    classname = db.Column(db.String(10), nullable=True)
    sex = db.Column(db.SmallInteger, default=0, nullable=False)
    province = db.Column(db.String(10), nullable=True)
    city = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(20), nullable=True)
    headimgurl = db.Column(db.String(150), nullable=True)
    regtime = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, openid, nickname=None, realname=None,
                 classname=None, sex=None, province=None, city=None,
                 country=None, headimgurl=None, regtime=None):
        self.openid = openid
        self.nickname = nickname
        self.realname = realname
        self.classname = classname
        self.sex = sex
        self.province = province
        self.city = city
        self.country = country
        self.headimgurl = headimgurl
        self.regtime = regtime

    def __repr__(self):
        return '<openid %r>' % self.openid

    def save(self):
        cache = redis.exists(redis_prefix + self.openid)
        if not cache:
            exist_in_db = User.query.filter_by(openid=self.openid).first()
            if exist_in_db is None:
                db.session.add(self)
                db.session.commit()
            # 写入缓存
            redis.hmset(redis_prefix + self.openid, {
                "nickname": self.nickname,
                "realname": self.realname,
                "classname": self.classname,
                "sex": self.sex,
                "province": self.province,
                "city": self.city,
                "country": self.country,
                "headimgurl": self.headimgurl,
                "regtime": self.regtime
            })
        return None
