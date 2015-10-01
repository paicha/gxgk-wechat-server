#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from main import wechat, app
from .models import set_user_info
from .plugins.state import *
from .plugins import simsimi


def wechat_response(data):
    """微信消息处理回复"""
    global message, openid

    wechat.parse_data(data)
    message = wechat.get_message()
    openid = message.source

    # 用户信息写入数据库
    set_user_info(openid)

    # 默认回复微信请求信息
    response = 'success'
    if message.type == 'text':
        # 替换全角空格为半角空格
        message.content = message.content.replace(u'　', ' ')
        # 清除行首空格
        message.content = message.content.lstrip()
        # TODO 繁体转换或增加繁体关键字判断
        # 指令列表
        commands = {
            u'取消': cancel_command,
            u'^\?|^？': all_command,
            u'^留言|^客服': leave_a_message,
            u'雷达': weather_radar,
            u'电话': phone_number,
            u'^公交|^公车': bus_routes,
            u'放假|校历': academic_calendar,
            u'合作': contact_us,
            u'明信片': postcard,
            u'游戏': html5_games,
            u'成绩': developing,
            u'新闻': developing,
            u'天气': developing,
            u'陪聊': enter_chat_state,
            u'四六级': developing,
            u'图书馆': developing,
            u'签到': developing,
            u'音乐': developing,
            u'论坛': developing,
            u'快递': developing,
            u'更新菜单': update_menu_setting
        }
        # 状态列表
        state_commands = {
            'chat': chat_robot
        }

        # 匹配指令
        command_match = False
        for key_word in commands:
            if re.match(key_word, message.content):
                # 指令匹配后，设置默认状态
                set_user_state(openid, 'default')
                response = commands[key_word]()
                command_match = True
                break
        if not command_match:
            # 匹配状态
            state = get_user_state(openid)
            # 关键词、状态都不匹配，缺省回复
            if state == 'default':
                response = command_not_found()
            else:
                response = state_commands[state]()

    elif message.type == 'click':
        commands = {
            'phone_number': phone_number,
            'score': developing,
            'express': developing,
            'search_books': developing,
            'chat_robot': enter_chat_state,
            'sign': developing,
            'music': developing,
            'weather': developing
        }
        # 匹配指令后，重置状态
        set_user_state(openid, 'default')
        response = commands[message.key]()

    elif message.type == 'subscribe':
        # 关注后，默认状态
        set_user_state(openid, 'default')
        response = subscribe()
    else:
        pass

    # 保存最后一次交互的时间
    set_user_last_interact_time(openid, message.time)
    return response


def developing():
    """维护公告"""
    return wechat.response_text('该功能维护中，过两天再来吧')


def cancel_command():
    content = app.config['CANCEL_COMMAND_TEXT'] + app.config['COMMAND_TEXT']
    return wechat.response_text(content)


def enter_chat_state():
    """进入聊天模式"""
    set_user_state(openid, 'chat')
    return wechat.response_text(app.config['ENTER_CHAT_STATE_TEXT'])


def chat_robot():
    """聊天机器人"""
    timeout = int(message.time) - int(get_user_last_interact_time(openid))
    # 超过一段时间，提示聊天超时
    if timeout > 5 * 60:
        set_user_state(openid, 'default')
        return wechat.response_text(app.config['CHAT_TIME_OUT_TEXT'])
    else:
        content = simsimi.chat(message.content)
        return wechat.response_text(content)


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


def all_command():
    """回复全部指令"""
    content = app.config['COMMAND_TEXT']
    return wechat.response_text(content)


def subscribe():
    """回复订阅事件"""
    content = app.config['WELCOME_TEXT'] + app.config['COMMAND_TEXT']
    return wechat.response_text(content)


def phone_number():
    """回复电话号码"""
    content = app.config['PHONE_NUMBER_TEXT'] + app.config['HELP_TEXT']
    return wechat.response_text(content)
