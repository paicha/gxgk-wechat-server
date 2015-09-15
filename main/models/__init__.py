#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from .. import app, wechat, redis

db = SQLAlchemy(app)

from .auth import *
from .express import *
from .sign import *
from .user import *


def set_user_info(openid):
    """保存用户信息"""
    redis_prefix = "wechat:user:"
    cache = redis.exists(redis_prefix + openid)

    if not cache:
        user_info = User.query.filter_by(openid=openid).first()
        if not user_info:
            user_info = wechat.get_user_info(openid)
            user = User(openid=user_info['openid'],
                        nickname=user_info['nickname'],
                        sex=user_info['sex'],
                        province=user_info['province'],
                        city=user_info['city'],
                        country=user_info['country'],
                        headimgurl=user_info['headimgurl'])
            user.save()
            # 与查询的数据类型一样，方便 redis 写入
            user_info = user

        # 写入缓存
        redis.hmset(redis_prefix + user_info.openid, {
            "nickname": user_info.nickname,
            "realname": user_info.realname,
            "classname": user_info.classname,
            "sex": user_info.sex,
            "province": user_info.province,
            "city": user_info.city,
            "country": user_info.country,
            "headimgurl": user_info.headimgurl,
            "regtime": user_info.regtime
        })

        return None
    else:
        return None
