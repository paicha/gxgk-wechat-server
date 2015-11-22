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


def get_sign_info(openid):
    """读取签到信息"""
    redis_prefix = "wechat:sign:"
    sign_info_cache = redis.hgetall(redis_prefix + openid)

    if not sign_info_cache:
        # 无缓存，查询数据库
        sign_info = Sign.query.filter_by(openid=openid).first()
        if not sign_info:
            return {
                "lastsigntime": 0,
                "keepdays": 0,
                "totaldays": 0
            }
        else:
            redis.hmset(redis_prefix + openid, {
                "lastsigntime": sign_info.lastsigntime,
                "keepdays": sign_info.keepdays,
                "totaldays": sign_info.totaldays
            })
            return {
                "lastsigntime": int(sign_info.lastsigntime),
                "keepdays": int(sign_info.keepdays),
                "totaldays": int(sign_info.totaldays)
            }
    else:
        return {
            "lastsigntime": int(sign_info_cache["lastsigntime"]),
            "keepdays": int(sign_info_cache["keepdays"]),
            "totaldays": int(sign_info_cache["totaldays"])
        }


def update_sign_info(openid, lastsigntime, totaldays, keepdays):
    """更新签到信息"""
    # 写入缓存
    redis_prefix = "wechat:sign:"
    redis.hmset(redis_prefix + openid, {
                "lastsigntime": lastsigntime,
                "totaldays": totaldays,
                "keepdays": keepdays
                })
    # 写入数据库
    sign_info = Sign.query.filter_by(openid=openid).first()
    if not sign_info:
        sign_info = Sign(openid, lastsigntime, totaldays, keepdays)
        sign_info.save()
    else:
        sign_info.lastsigntime = lastsigntime
        sign_info.totaldays = totaldays
        sign_info.keepdays = keepdays
        sign_info.update()

    return None


def get_today_sign_ranklist(today_timestamp):
    """获取今日签到排行榜"""
    data = Sign.query.join(User, Sign.openid == User.openid) \
        .add_columns(User.nickname) \
        .filter(Sign.lastsigntime >= today_timestamp) \
        .order_by(Sign.lastsigntime).all()

    return data


def get_sign_keepdays_ranklist():
    """获取续签排行榜"""
    data = Sign.query.join(User, Sign.openid == User.openid) \
        .add_columns(User.nickname) \
        .order_by(Sign.keepdays.desc()).all()

    return data


def get_express_num(openid, num):
    """读取快递信息"""
    express_info = Express.query.filter_by(openid=openid, num=num).first()
    return express_info


def set_express_num(openid, num, com_code, lastupdate, ischeck):
    """写入快递信息"""
    express_info = get_express_num(openid, num)
    if not express_info:
        express = Express(openid=openid,
                          num=num,
                          comcode=com_code,
                          lastupdate=lastupdate,
                          ischeck=ischeck)
        express.save()
    else:
        if express_info.lastupdate != lastupdate:
            express_info.lastupdate = lastupdate
            express_info.ischeck = ischeck
            express_info.update()


def get_uncheck_express():
    """读取未签收的快递信息"""
    express_info = Express.query.filter_by(ischeck=0).all()
    return express_info


def get_user_student_info(openid):
    """读取绑定的教务平台账号"""
    redis_prefix = "wechat:user:"
    user_info_cache = redis.hgetall(redis_prefix + openid)

    if 'studentid' in user_info_cache and 'studentpwd' in user_info_cache:
        return user_info_cache
    else:
        auth_info = Auth.query.filter_by(openid=openid).first()
        if auth_info and auth_info.studentid and auth_info.studentpwd:
            # 写入缓存
            redis.hmset(redis_prefix + openid, {
                "studentid": auth_info.studentid,
                "studentpwd": auth_info.studentpwd,
            })
            user_info_cache['studentid'] = auth_info.studentid
            user_info_cache['studentpwd'] = auth_info.studentpwd
            return user_info_cache
        else:
            return False
