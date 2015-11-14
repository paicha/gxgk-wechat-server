#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, abort
from . import app, wechat, redis
from .utils import check_signature
from .response import wechat_response


@app.route("/", methods=['GET', 'POST'])
@check_signature
def handle_wechat_request():
    """
    处理回复微信请求
    """
    if request.method == 'POST':
        return wechat_response(request.data)
    else:
        # 微信接入验证
        return request.args.get('echostr', '')


@app.route('/update_access_token', methods=["GET"])
def update_access_token():
    """
    读取微信最新 access_token，写入缓存
    """
    if request.remote_addr == '127.0.0.1':
        # 获取 access_token
        token = wechat.grant_token()
        access_token = token['access_token']
        # 存入缓存，设置过期时间
        redis.set("wechat:access_token", access_token, 7000)
        return ('', 204)
    else:
        abort(404)


@app.errorhandler(404)
def page_not_found(error):
    return "page not found!"
