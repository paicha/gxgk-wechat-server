#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, render_template, jsonify, Markup
from . import app, wechat, redis
from .utils import check_signature, get_jsapi_signature_data
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


@app.route('/auth-score', methods=['POST'])
@app.route('/auth-score/<openid>')
def auth_score(openid=None):
    """教务系统绑定"""
    if request.method == 'POST':
        return jsonify(**{'errcode': 0, 'errmsg': 'ok'})
    else:
        jsapi = get_jsapi_signature_data('request.url')
        jsapi['jsApiList'] = ['hideOptionMenu']
        return render_template('auth.html',
                               title=u'微信查成绩',
                               desc=u'请先绑定教务系统',
                               username_label=u'学号',
                               username_label_placeholder=u'请输入你的学号',
                               password_label_placeholder=u'默认是身份证号码',
                               openid=openid,
                               jsapi=Markup(jsapi))


@app.route('/auth-library', methods=['POST'])
@app.route('/auth-library/<openid>')
def auth_library(openid=None):
    """借书卡账号绑定"""
    if request.method == 'POST':
        return jsonify(**{'errcode': 0, 'errmsg': 'ok'})
    else:
        jsapi = get_jsapi_signature_data('request.url')
        jsapi['jsApiList'] = ['hideOptionMenu']
        return render_template('auth.html',
                               title=u'图书馆查询',
                               desc=u'请先绑定借书卡',
                               username_label=u'卡号',
                               username_label_placeholder=u'请输入你的借书卡号',
                               password_label_placeholder=u'默认是 123456',
                               openid=openid,
                               jsapi=Markup(jsapi))


@app.route(app.config['UPDATE_ACCESS_TOKEN_URL_ROUTE'], methods=["GET"])
def update_access_token():
    """
    读取微信最新 access_token，写入缓存
    """
    # 获取 access_token
    token = wechat.grant_token()
    access_token = token['access_token']
    # 存入缓存，设置过期时间
    redis.set("wechat:access_token", access_token, 7000)
    return ('', 204)


@app.errorhandler(404)
def page_not_found(error):
    return "page not found!"
