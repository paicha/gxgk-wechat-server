#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = False

MAIN_URL = "http://bbs.gxgk.cc/wechat/"

WELCOME_TEXT = u"感谢关注莞香广科[愉快]\n我是广科助手小喵[调皮]\n\n"

COMMAND_TEXT = u"请回复以下关键词开始：\n——————————\n成绩  图书馆  四六级\n\n电话  快递  明信片\n\n签到  音乐  游戏\n\n公交  雷达  天气\n\n校历  新闻  论坛\n\n陪聊  留言  合作\n\n点击左下角切换菜单"

COMMAND_NOT_FOUND_TEXT = u"收到你的留言啦！"

CANCEL_COMMAND_TEXT = u"已回到正常模式啦啦啦~\n\n"

HELP_TEXT = u"\n\n回复 “ ? ” 查看主菜单"

BBS_URL_TXT = u'点击：<a href="http://wsq.discuz.qq.com/?siteid=264557099">进入论坛</a>'

PHONE_NUMBER_TEXT = u"————办公————\n校园网 0769-86211959\n\n院办室 0769-86211800\n\n学生处 0769-86211913\n\n教务处 0769-86211915\n\n招生办 0769-86211555"

LEAVE_A_MESSAGE_TEXT = u"Hi~这里是小喵~\n请听到喵一声之后留言\n\n喵~回复：m+内容\n如：m小喵是笨蛋"

WEATHER_RADAR_TEXT = u'点击查看：<a href="http://www.dg121.com/tianqiziliao/donghua_yun_radar/radar.gif">东莞雷达回波</a>'

HTML5_GAMES_TEXT = u'点击：<a href="http://autobox.meiriq.com/list/302da1ab?from=gxgkcat">开始玩游戏</a>'

POSTCARD_TEXT = u'点击：<a href="https://jinshuju.net/s/iBxE0L">明信片查询</a>'

CONTACT_US_TEXT = u"我们欢迎各类型的合作\n　\n请联系：weixin@gxgk.cc\nQQ：646304004"

ENTER_CHAT_STATE_TEXT = u"已进入自动陪聊模式\n回复你想要说的话吧\n\n回复“取消”退出陪聊\n若留言请回复m+内容"

ENTER_EXPRESS_STATE_TEXT = u"已进入快递查询模式\n\n直接回复运单号\n即可查询物流信息\n\n回复“取消”退出本模式"

BUS_ROUTES_NEWS = [{
    'title': u'公交路线时刻表',
    'description': u'没时间解释，快上车！',
    'picurl': 'http://mmsns.qpic.cn/mmsns/8KFpmUicXXiaozFvzPpwulLf1eqcgMzUmO8yjjNybHhbJUxUwkthQWxQ/0',
    'url': u'http://mp.weixin.qq.com/mp/appmsg/show?__biz=MjM5NTY3NjAyMg==&appmsgid=10000022&itemidx=1&sign=4015ca2f093456d0b51a4e7b5663a242#wechat_redirect'
}]

ACADEMIC_CALENDAR_NEWS = [{
    'title': u'学院校历',
    'picurl': 'http://mmsns.qpic.cn/mmsns/8KFpmUicXXiapGAN4IVROwL5D7WnnN1UpbMUlno5AQxmmwwbac8dugVQ/0',
    'url': u'http://mp.weixin.qq.com/s?__biz=MjM5NTY3NjAyMg==&mid=200033329&idx=1&sn=68e442607cd923a9ae6bdad7fc3be6d0#rd',
}]

MENU_SETTING = {
    "button": [
        {
            "name": "校园生活",
            "sub_button": [
                {
                    "type": "view",
                    "name": "广科论坛",
                    "url": "http://wsq.discuz.qq.com/?siteid=264557099",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "常用电话",
                    "key": "phone_number",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "单号查快递",
                    "key": "express",
                    "sub_button": []
                },
                {
                    "type": "scancode_waitmsg",
                    "name": "扫码查快递",
                    "key": "scan_express_code",
                    "sub_button": []
                }
            ]
        },
        {
            "name": "我是学霸",
            "sub_button": [
                {
                    "type": "click",
                    "name": "成绩查询",
                    "key": "score",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "图书馆找书",
                    "key": "search_books",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "借书记录",
                    "key": "borrowing_record",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "一键续借",
                    "key": "renew_books",
                    "sub_button": []
                }
            ]
        },
        {
            "name": "ฅ'ω'ฅ",
            "sub_button": [
                {
                    "type": "click",
                    "name": "每日签到",
                    "key": "sign",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "小喵陪聊",
                    "key": "chat_robot",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "听一首歌",
                    "key": "music",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "东莞天气",
                    "key": "weather",
                    "sub_button": []
                }
            ]
        }
    ]
}
