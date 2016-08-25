#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from flask.ext.sqlalchemy import SQLAlchemy
from .. import app, redis
from ..utils import init_wechat_sdk
from ..plugins.state import get_user_last_interact_time

db = SQLAlchemy(app)

from .auth import Auth
from .express import Express
from .sign import Sign
from .user import User


def set_user_info(openid):
    """保存用户信息"""
    redis_prefix = "wechat:user:"
    cache = redis.hexists(redis_prefix + openid, 'nickname')

    if not cache:
        user_info = User.query.filter_by(openid=openid).first()
        if not user_info:
            try:
                wechat = init_wechat_sdk()
                user_info = wechat.get_user_info(openid)
                if 'nickname' not in user_info:
                    raise KeyError(user_info)
            except Exception, e:
                app.logger.warning(u"获取微信用户信息 API 出错: %s" % e)
                user_info = None
            else:
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

        if user_info:
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
    else:
        timeout = int(time.time()) - int(get_user_last_interact_time(openid))
        if timeout > 24 * 60 * 60:
            try:
                wechat = init_wechat_sdk()
                user_info = wechat.get_user_info(openid)
                if 'nickname' not in user_info:
                    raise KeyError(user_info)
            except Exception, e:
                app.logger.warning(u"获取微信用户信息 API 出错: %s" % e)
            else:
                user = User.query.filter_by(openid=openid).first()
                user.nickname = user_info['nickname']
                user.sex = user_info['sex']
                user.province = user_info['province']
                user.city = user_info['city']
                user.country = user_info['country']
                user.headimgurl = user_info['headimgurl']
                user.update()

                redis.hmset(redis_prefix + openid, {
                    "nickname": user_info['nickname'],
                    "sex": user_info['sex'],
                    "province": user_info['province'],
                    "city": user_info['city'],
                    "country": user_info['country'],
                    "headimgurl": user_info['headimgurl']
                })
        return None


def is_user_exists(openid):
    """用户是否存在数据库"""
    redis_prefix = "wechat:user:"
    cache = redis.exists(redis_prefix + openid)
    if not cache:
        user_info = User.query.filter_by(openid=openid).first()
        if not user_info:
            return False
        else:
            return True
    else:
        return True


def get_sign_info(openid):
    """读取签到信息"""
    sign_info = Sign.query.filter_by(openid=openid).first()
    if not sign_info:
        return {
            "lastsigntime": 0,
            "keepdays": 0,
            "totaldays": 0
        }
    else:
        return {
            "lastsigntime": int(sign_info.lastsigntime),
            "keepdays": int(sign_info.keepdays),
            "totaldays": int(sign_info.totaldays)
        }


def update_sign_info(openid, lastsigntime, totaldays, keepdays):
    """更新签到信息"""
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


def get_sign_keepdays_ranklist(today_timestamp):
    """获取续签排行榜"""
    data = Sign.query.join(User, Sign.openid == User.openid) \
        .add_columns(User.nickname) \
        .filter(Sign.lastsigntime >= today_timestamp) \
        .order_by(Sign.keepdays.desc(),
                  Sign.totaldays.desc(),
                  Sign.lastsigntime).limit(6).all()

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


def get_all_uncheck_express():
    """读取未签收的快递信息"""
    express_info = Express.query.filter(Express.ischeck != 3).all()
    return express_info


def get_all_auth_info():
    """读取全部授权账号信息"""
    auth_info = Auth.query.all()
    return auth_info


def get_user_student_info(openid):
    """读取绑定的教务管理系统账号"""
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


def get_user_library_info(openid):
    """读取绑定的图书馆账号"""
    redis_prefix = "wechat:user:"
    user_info_cache = redis.hgetall(redis_prefix + openid)

    if 'libraryid' in user_info_cache and 'librarypwd' in user_info_cache:
        return user_info_cache
    else:
        auth_info = Auth.query.filter_by(openid=openid).first()
        if auth_info and auth_info.libraryid and auth_info.librarypwd:
            # 写入缓存
            redis.hmset(redis_prefix + openid, {
                "libraryid": auth_info.libraryid,
                "librarypwd": auth_info.librarypwd,
            })
            user_info_cache['libraryid'] = auth_info.libraryid
            user_info_cache['librarypwd'] = auth_info.librarypwd
            return user_info_cache
        else:
            return False


def set_user_student_info(openid, studentid, studentpwd):
    """写入绑定的教务管理系统账号"""
    redis_prefix = "wechat:user:"
    auth_info = Auth.query.filter_by(openid=openid).first()
    if not auth_info:
        auth = Auth(openid=openid,
                    studentid=studentid,
                    studentpwd=studentpwd)
        auth.save()
    else:
        auth_info.studentid = studentid
        auth_info.studentpwd = studentpwd
        auth_info.update()

    # 写入缓存
    redis.hmset(redis_prefix + openid, {
        "studentid": studentid,
        "studentpwd": studentpwd
    })


def set_user_library_info(openid, libraryid, librarypwd):
    """写入绑定的借书卡账号"""
    redis_prefix = "wechat:user:"
    auth_info = Auth.query.filter_by(openid=openid).first()
    if not auth_info:
        auth = Auth(openid=openid,
                    libraryid=libraryid,
                    librarypwd=librarypwd)
        auth.save()
    else:
        auth_info.libraryid = libraryid
        auth_info.librarypwd = librarypwd
        auth_info.update()

    # 写入缓存
    redis.hmset(redis_prefix + openid, {
        "libraryid": libraryid,
        "librarypwd": librarypwd
    })


def set_user_realname_and_classname(openid, realname, classname):
    """写入用户的真实姓名和班级"""
    redis_prefix = "wechat:user:"
    user_info_cache = redis.hgetall(redis_prefix + openid)
    realname_exists = redis.hexists(redis_prefix + openid, 'realname')

    if not realname_exists or user_info_cache['realname'] != realname.encode('utf-8'):
        user_info = User.query.filter_by(openid=openid).first()
        if user_info:
            user_info.realname = realname
            user_info.classname = classname
            user_info.update()
        # 写入缓存
        redis.hmset(redis_prefix + openid, {
            "realname": realname,
            "classname": classname
        })
