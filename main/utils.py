#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from flask import request, redirect
from . import app, wechat, redis
import time
import random
import string


def check_signature(func):
    """
    微信签名验证
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')

        if not wechat.check_signature(signature=signature,
                                      timestamp=timestamp,
                                      nonce=nonce):
            if request.method == 'POST':
                return "signature failed"
            else:
                return redirect(app.config['MAIN_URL'])

        return func(*args, **kwargs)

    return decorated_function


def get_wechat_access_token():
    """获取 access_token"""
    access_token = redis.get("wechat:access_token")
    if access_token:
        return access_token
    else:
        app.logger.warning(u"获取 access_token 缓存失败")
        return None


def get_jsapi_signature_data(url):
    """
    获取 jsapi 前端签名数据
    """
    timestamp = int(time.time())
    noncestr = generate_random_str(16)
    signature = wechat.generate_jsapi_signature(timestamp, noncestr, url)
    return {
        "appId": app.config['APP_ID'],
        "timestamp": timestamp,
        "nonceStr": noncestr,
        "signature": signature,
    }


def generate_random_str(N):
    """生成随机字符串"""
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
