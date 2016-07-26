#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, render_template, jsonify, Markup, abort, \
    send_from_directory
from . import app, redis
from .utils import check_signature, get_jsapi_signature_data
from .response import wechat_response
from .plugins import score, library
from .models import is_user_exists
import ast


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
            score.get_info.delay(openid, studentid, studentpwd, check_login=True)
            errmsg = 'ok'
        else:
            errmsg = u'学号或者密码格式不合法'
        return jsonify({'errmsg': errmsg})
    elif is_user_exists(openid):
        jsapi = get_jsapi_signature_data(request.url)
        jsapi['jsApiList'] = ['hideAllNonBaseMenuItem']
        return render_template('auth.html',
                               title=u'微信查成绩',
                               desc=u'请绑定教务系统，请勿分享本页面',
                               username_label=u'学号',
                               username_label_placeholder=u'请输入你的学号',
                               password_label_placeholder=u'默认是身份证号码',
                               baidu_analytics=app.config['BAIDU_ANALYTICS'],
                               jsapi=Markup(jsapi))
    else:
        abort(404)


@app.route('/auth-score/<openid>/result', methods=['GET'])
def auth_score_result(openid=None):
    """查询学号绑定结果"""
    if is_user_exists(openid):
        redis_prefix = 'wechat:user:auth:score:'
        errmsg = redis.get(redis_prefix + openid)
        if errmsg:
            redis.delete(redis_prefix + openid)
            return jsonify({'errmsg': errmsg})
        else:
            abort(404)
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
            library.borrowing_record.delay(openid, libraryid, librarypwd, check_login=True)
            errmsg = 'ok'
        else:
            errmsg = u'卡号或者密码格式不合法'
        return jsonify({'errmsg': errmsg})
    elif is_user_exists(openid):
        jsapi = get_jsapi_signature_data(request.url)
        jsapi['jsApiList'] = ['hideAllNonBaseMenuItem']
        return render_template('auth.html',
                               title=u'图书馆查询',
                               desc=u'请绑定借书卡，请勿分享本页面',
                               username_label=u'卡号',
                               username_label_placeholder=u'请输入你的借书卡号',
                               password_label_placeholder=u'默认是卡号后六位',
                               baidu_analytics=app.config['BAIDU_ANALYTICS'],
                               jsapi=Markup(jsapi))
    else:
        abort(404)


@app.route('/auth-library/<openid>/result', methods=['GET'])
def auth_library_result(openid=None):
    """查询借书卡绑定结果"""
    if is_user_exists(openid):
        redis_prefix = 'wechat:user:auth:library:'
        errmsg = redis.get(redis_prefix + openid)
        if errmsg:
            redis.delete(redis_prefix + openid)
            return jsonify({'errmsg': errmsg})
        else:
            abort(404)
    else:
        abort(404)


@app.route('/score-report/<openid>', methods=['GET'])
def school_report_card(openid=None):
    """学生成绩单"""
    if is_user_exists(openid):
        jsapi = get_jsapi_signature_data(request.url)
        jsapi['jsApiList'] = ['onMenuShareTimeline',
                              'onMenuShareAppMessage',
                              'onMenuShareQQ',
                              'onMenuShareWeibo',
                              'onMenuShareQZone']
        score_cache = redis.hgetall('wechat:user:scoreforweb:' + openid)
        if score_cache:
            score_info = ast.literal_eval(score_cache['score_info'])
            real_name = score_cache['real_name'].decode('utf-8')
            return render_template('score.html',
                                   real_name=real_name,
                                   school_year=score_cache['school_year'],
                                   school_term=score_cache['school_term'],
                                   score_info=score_info,
                                   update_time=score_cache['update_time'],
                                   baidu_analytics=app.config[
                                       'BAIDU_ANALYTICS'],
                                   jsapi=Markup(jsapi))
        else:
            # 一般不会丢失缓存数据
            # 若丢失，用户再一次查询成功就有缓存了
            abort(404)
    else:
        abort(404)


@app.route('/robots.txt')
def robots():
    """搜索引擎爬虫协议"""
    return send_from_directory(app.static_folder, request.path[1:])


@app.errorhandler(404)
def page_not_found(error):
    return "page not found!", 404


@app.errorhandler(Exception)
def unhandled_exception(error):
    app.logger.error('Unhandled Exception: %s', (error))
    return "Error", 500
