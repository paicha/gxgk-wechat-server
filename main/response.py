#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
from main import wechat, app
from .models import set_user_info, get_user_student_info
from .utils import AESCipher
from .plugins.state import *
from .plugins import simsimi
from .plugins import sign
from .plugins import express
from .plugins import music
from .plugins import score


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
            u'^m': command_not_found,
            u'雷达': weather_radar,
            u'电话': phone_number,
            u'^公交|^公车': bus_routes,
            u'放假|校历': academic_calendar,
            u'合作': contact_us,
            u'明信片': postcard,
            u'游戏': html5_games,
            u'成绩': exam_grade,
            u'新闻': developing,
            u'天气': developing,
            u'陪聊': enter_chat_state,
            u'四六级': developing,
            u'图书馆': developing,
            u'^签到|^起床': daily_sign,
            u'音乐': play_music,
            u'论坛': bbs_url,
            u'快递': enter_express_state,
            u'绑定': auth_url,
            u'更新菜单': update_menu_setting
        }
        # 状态列表
        state_commands = {
            'chat': chat_robot,
            'express': express_shipment_tracking
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
            if state == 'default' or not state:
                response = command_not_found()
            else:
                response = state_commands[state]()

    elif message.type == 'click':
        commands = {
            'phone_number': phone_number,
            'bus': bus_routes,
            'score': exam_grade,
            'cet': developing,
            'express': enter_express_state,
            'search_books': developing,
            'borrowing_record': developing,
            'renew_books': developing,
            'chat_robot': enter_chat_state,
            'sign': daily_sign,
            'music': play_music,
            'weather': developing
        }
        # 匹配指令后，重置状态
        set_user_state(openid, 'default')
        response = commands[message.key]()

    elif message.type == 'scancode_waitmsg':
        set_user_state(openid, 'express')
        response = express_shipment_tracking()

    elif message.type == 'subscribe':
        # 关注后，默认状态
        set_user_state(openid, 'default')
        response = subscribe()
    else:
        pass

    # 保存最后一次交互的时间
    set_user_last_interact_time(openid, message.time)
    return response


def exam_grade():
    """查询期末成绩"""
    user_student_info = get_user_student_info(openid)
    if user_student_info:
        # 解密密码
        cipher = AESCipher(app.config['PASSWORD_SECRET_KEY'])
        studentpwd = cipher.decrypt(user_student_info['studentpwd'])
        score.get_info.delay(openid, user_student_info['studentid'], studentpwd)
        return wechat.response_text('查询中……')
    else:
        url = app.config['HOST_URL'] + '/auth-score/' + openid
        content = u'请先绑定学号\n\n<a href="%s">【点击这里绑定学号】</a>' % url +\
            u'\n\n绑定后即可查询\n\n高峰时期如果无反应\n请重试几次'
        return wechat.response_text(content)


def express_shipment_tracking():
    """快递物流查询"""
    if message.type == 'text':
        timeout = int(message.time) - int(get_user_last_interact_time(openid))
        # 超过一段时间，退出模式
        if timeout > 15 * 60:
            set_user_state(openid, 'default')
            content = app.config['COMMAND_NOT_FOUND_TEXT'] + \
                u'\n\n回复 “快递” 进入查询快递模式' + app.config['HELP_TEXT']
            return wechat.response_text(content)
        else:
            # 放入队列任务执行，异步回复
            express.get_tracking_info.delay(openid, message.content)
            # 立即返回
            return 'success'
    else:
        if message.ScanCodeInfo[0]['ScanType'] == 'barcode':
            # 读取条形码扫描的单号
            num = message.ScanCodeInfo[0]['ScanResult'].split(",", 1)[1]
            # 异步查询
            express.get_tracking_info.delay(openid, num)
            return 'success'
        else:
            return wechat.response_text('识别错误，请扫描快递条形码')


def play_music():
    """随机音乐"""
    music.get_douban_fm.delay(openid)
    return 'success'


def chat_robot():
    """聊天机器人"""
    timeout = int(message.time) - int(get_user_last_interact_time(openid))
    # 超过一段时间，退出模式
    if timeout > 20 * 60:
        set_user_state(openid, 'default')
        return command_not_found()
    else:
        simsimi.chat.delay(openid, message.content)
        return 'success'


def daily_sign():
    """每日签到"""
    data = sign.daily_sign(openid)
    if data:
        wechat.send_template_message(
            openid, app.config['SIGN_TEMPLATE_ID'], data['template_data'])
        # 为保证模板通知先被接收
        time.sleep(0.7)
        return wechat.response_text(data['ranklist'])
    else:
        return wechat.response_text(u"离起床还早呢~\n快睡觉吧~\n\n签到时间从" +
                                    u"早上6点开始\n\n记得每天签到啦~")


def auth_url():
    """教务系统、图书馆绑定的 URL"""
    jw_url = app.config['HOST_URL'] + '/auth-score/' + openid
    library_url = app.config['HOST_URL'] + '/auth-library/' + openid
    content = u'<a href="%s">教务系统绑定：点击这里</a>\n\n\n' % jw_url +\
        u'<a href="%s">图书馆系统绑定：点击这里</a>' % library_url
    return wechat.response_text(content)


def update_menu_setting():
    """更新自定义菜单"""
    try:
        wechat.create_menu(app.config['MENU_SETTING'])
    except Exception, e:
        return wechat.response_text(e)
    else:
        return wechat.response_text('Done!')


def developing():
    """维护公告"""
    return wechat.response_text('该功能维护中，过两天再来吧')


def enter_express_state():
    """进入快递查询模式"""
    set_user_state(openid, 'express')
    return wechat.response_text(app.config['ENTER_EXPRESS_STATE_TEXT'])


def cancel_command():
    """取消状态"""
    content = app.config['CANCEL_COMMAND_TEXT'] + app.config['COMMAND_TEXT']
    return wechat.response_text(content)


def enter_chat_state():
    """进入聊天模式"""
    set_user_state(openid, 'chat')
    return wechat.response_text(app.config['ENTER_CHAT_STATE_TEXT'])


def postcard():
    """明信片查询"""
    content = app.config['POSTCARD_TEXT'] + app.config['HELP_TEXT']
    return wechat.response_text(content)


def html5_games():
    """HTML5游戏"""
    content = app.config['HTML5_GAMES_TEXT'] + app.config['HELP_TEXT']
    return wechat.response_text(content)


def contact_us():
    """合作信息"""
    content = app.config['CONTACT_US_TEXT'] + app.config['HELP_TEXT']
    return wechat.response_text(content)


def academic_calendar():
    """校历"""
    return wechat.response_news(app.config['ACADEMIC_CALENDAR_NEWS'])


def bbs_url():
    """论坛网址"""
    content = app.config['BBS_URL_TXT'] + app.config['HELP_TEXT']
    return wechat.response_text(content)


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
    content = app.config['COMMAND_NOT_FOUND_TEXT'] + app.config['HELP_TEXT']
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
