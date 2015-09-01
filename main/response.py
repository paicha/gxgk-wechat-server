#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from main import wechat, app


def wechat_response(data):
    """微信消息处理回复"""
    wechat.parse_data(data)
    message = wechat.get_message()
    # TODO 用户信息写入数据库
    response = 'success'
    if message.type == 'text':
        # 替换全角空格为半角空格
        message.content = message.content.replace(u'　', ' ')
        # 清除行首空格
        message.content = message.content.lstrip()

        if message.content == u'电话':
            response = phone_number()
        elif re.match(u'^留言|^客服', message.content):
            response = leave_a_message()
        elif message.content == u'雷达':
            response = weather_radar()
        elif re.match(u'^公交|^公车', message.content):
            response = bus_routes()
        elif re.match(u'放假|校历', message.content):
            response = academic_calendar()
        elif message.content == u'合作':
            response = contact_us()
        elif message.content == u'明信片':
            response = postcard()
        elif message.content == u'成绩':
            response = wechat.response_text('成绩功能测试中')
        elif message.content == u'新闻':
            response = wechat.response_text('新闻功能测试中')
        elif message.content == u'四六级':
            response = wechat.response_text('四六级功能测试中')
        elif message.content == u'签到':
            response = wechat.response_text('签到功能测试中')
        elif message.content == u'音乐':
            response = wechat.response_text('音乐功能测试中')
        elif message.content == u'论坛':
            response = wechat.response_text('论坛功能测试中')
        elif message.content == u'快递':
            response = wechat.response_text('快递功能测试中')
        elif message.content == u'更新菜单':
            response = update_menu_setting()
        else:
            response = command_not_found()
    elif message.type == 'click':
        if message.key == 'phone_number':
            response = phone_number()
        elif message.key == 'score':
            response = wechat.response_text('成绩功能测试中')
    elif message.type == 'subscribe':
        response = subscribe()
    else:
        pass

    return response


def update_menu_setting():
    """更新自定义菜单"""
    try:
        wechat.create_menu(app.config['MENU_SETTING'])
    except Exception, e:
        return wechat.response_text(e)
    else:
        return wechat.response_text('Done!')


def postcard():
    """明信片查询"""
    return wechat.response_text(app.config['POSTCARD_TEXT'])


def html5_games():
    """HTML5游戏"""
    return wechat.response_text(app.config['HTML5_GAMES_TEXT'])


def contact_us():
    """合作信息"""
    content = app.config['CONTACT_US_TEXT'] + app.config['HELP_TEXT']
    return wechat.response_text(content)


def academic_calendar():
    """校历"""
    return wechat.response_news(app.config['ACADEMIC_CALENDAR_NEWS'])


def bus_routes():
    """公交信息"""
    return wechat.response_news(app.config['BUS_ROUTES_NEWS'])


def weather_radar():
    """气象雷达动态图"""
    content = app.config['WEATHER_RADAR_TEXT'] + app.config['HELP_TEXT']
    return wechat.response_text(content)


def leave_a_message():
    """留言提示"""
    content = app.config['LEAVE_A_MESSAGE_TEXT'] + app.config['HELP_TEXT']
    return wechat.response_text(content)


def command_not_found():
    """非关键词回复"""
    content = app.config['COMMAND_NOT_FOUND_TEXT'] + app.config['COMMAND_TEXT']
    return wechat.response_text(content)


def subscribe():
    """回复订阅事件"""
    content = app.config['WELCOME_TEXT'] + app.config['COMMAND_TEXT']
    return wechat.response_text(content)


def phone_number():
    """回复电话号码"""
    content = app.config['PHONE_NUMBER_TEXT'] + app.config['HELP_TEXT']
    return wechat.response_text(content)
