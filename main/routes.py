#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, render_template, jsonify, Markup, abort
from . import app, wechat, redis
from .utils import check_signature, get_jsapi_signature_data
from .response import wechat_response
from .plugins import score, library
from .models import is_user_exists


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


@app.route('/auth-score/<openid>', methods=['GET', 'POST'])
def auth_score(openid=None):
    """教务系统绑定"""
    if request.method == 'POST':
        studentid = request.form.get('studentid', '')
        studentpwd = request.form.get('studentpwd', '')
        # 根据用户输入的信息，模拟登陆
        if studentid and studentpwd and is_user_exists(openid):
            errmsg = score.get_info(
                openid, studentid, studentpwd, check_login=True)
        else:
            errmsg = u'学号或者密码格式不合法'
        return jsonify({'errmsg': errmsg})
    elif is_user_exists(openid):
        jsapi = get_jsapi_signature_data('request.url')
        jsapi['jsApiList'] = ['hideOptionMenu']
        return render_template('auth.html',
                               title=u'微信查成绩',
                               desc=u'请先绑定教务系统',
                               username_label=u'学号',
                               username_label_placeholder=u'请输入你的学号',
                               password_label_placeholder=u'默认是身份证号码',
                               jsapi=Markup(jsapi))
    else:
        abort(404)


@app.route('/auth-library/<openid>', methods=['GET', 'POST'])
def auth_library(openid=None):
    """借书卡账号绑定"""
    if request.method == 'POST':
        libraryid = request.form.get('libraryid', '')
        librarypwd = request.form.get('librarypwd', '')
        # 根据用户输入的信息，模拟登陆
        if libraryid and librarypwd and is_user_exists(openid):
            errmsg = library.borrowing_record(
                openid, libraryid, librarypwd, check_login=True)
        else:
            errmsg = u'卡号或者密码格式不合法'
        return jsonify({'errmsg': errmsg})
    elif is_user_exists(openid):
        jsapi = get_jsapi_signature_data('request.url')
        jsapi['jsApiList'] = ['hideOptionMenu']
        return render_template('auth.html',
                               title=u'图书馆查询',
                               desc=u'请先绑定借书卡',
                               username_label=u'卡号',
                               username_label_placeholder=u'请输入你的借书卡号',
                               password_label_placeholder=u'默认是卡号后六位',
                               jsapi=Markup(jsapi))
    else:
        abort(404)


@app.route(app.config['UPDATE_ACCESS_TOKEN_URL_ROUTE'], methods=["GET"])
def update_access_token():
    """
    读取微信最新 access_token，写入缓存
    """
    # 由于 wechat-python-sdk 中，generate_jsapi_signature -> grant_jsapi_ticket
    # 会顺带把 access_token 刷新了，所以先 grant_jsapi_ticket 再读取 access_token
    wechat.grant_jsapi_ticket()
    token = wechat.get_access_token()
    access_token = token['access_token']
    # 存入缓存，设置过期时间
    redis.set("wechat:access_token", access_token, 7000)
    return ('', 204)


@app.errorhandler(404)
def page_not_found(error):
    return "page not found!"
