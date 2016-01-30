#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = False

MAIN_URL = "http://weixin.gxgk.cc/"

WELCOME_TEXT = u"感谢关注莞香广科[愉快]\n我是广科助手小喵[调皮]\n\n"

COMMAND_TEXT = u"请回复以下关键词开始：\n——————————\n成绩  图书馆  四六级\n\n电话  快递  明信片\n\n签到  音乐  游戏\n\n公交  雷达  天气\n\n校历  新闻  论坛\n\n陪聊  合作\n\n点击左下角切换输入框"

COMMAND_NOT_FOUND_TEXT = u"收到你的留言啦！"

CANCEL_COMMAND_TEXT = u"已回到正常模式啦啦啦~\n\n"

HELP_TEXT = u"\n\n回复 “ ? ” 查看主菜单"

BBS_URL_TXT = u'<a href="http://wsq.discuz.qq.com/?siteid=264557099">进入论坛：点击这里</a>'

PHONE_NUMBER_TEXT = u"————办公————\n校园网 0769-86211959\n\n院办室 0769-86211800\n\n学生处 0769-86211913\n\n教务处 0769-86211915\n\n招生办 0769-86211555"

WEATHER_RADAR_TEXT = u'<a href="http://www.dg121.com/tianqiziliao/donghua_yun_radar/radar.gif">东莞雷达回波：点击这里</a>'

HTML5_GAMES_TEXT = u'<a href="http://autobox.meiriq.com/list/302da1ab?from=gxgkcat">开始玩游戏：点击这里</a>'

LIBRARY_TEXT = u'<a href="http://61.142.33.201:8090/sms/opac/search/showiphoneSearch.action">搜索图书馆书籍：点击这里</a>\n\n回复“借书”\n查询借书记录\n\n回复“续借”\n将7天内到期的书籍续借30天'

AUTH_JW_TEXT = u'<a href="%s">【点击这里绑定学号】</a>\n\n绑定后即可查询'

AUTH_LIBRARY_TEXT = u'<a href="%s">【点击这里绑定借书卡】</a>\n\n绑定后即可查询'

NOT_SIGN_TIME_TEXT = u"离起床还早呢~\n快睡觉吧~\n\n签到时间从早上6点开始\n\n记得每天签到啦~"

AUTH_TEXT = u'<a href="%s">教务系统绑定：点击这里</a>\n\n\n<a href="%s">图书馆系统绑定：点击这里</a>'

POSTCARD_TEXT = u'<a href="https://jinshuju.net/s/iBxE0L">明信片查询：点击这里</a>'

CET_SCORE_TEXT = u'<a href="http://115.159.64.43/CETQuery/">四六级查询：点击这里</a>'

CONTACT_US_TEXT = u"我们欢迎各类型的合作\n\n请联系：weixin@gxgk.cc\nQQ：646304004"

ENTER_CHAT_STATE_TEXT = u"已进入自动陪聊模式\n回复你想要说的话吧\n\n回复“取消”退出陪聊"

CHAT_TIMEOUT_TEXT = u"那么久不理小喵[可怜]\n自动退出陪聊模式啦~\n\n回复“陪聊”可以重新进入"

EXPRESS_TIMEOUT_TEXT = u'自动退出快递查询模式啦\n\n回复“快递”重新进入查询'

ENTER_EXPRESS_STATE_TEXT = u"已进入快递查询模式\n\n直接回复运单号\n即可查询快递信息\n\n回复“取消”退出本模式"

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
                }, {
                    "type": "view",
                    "name": "公交路线",
                    "url": "http://mp.weixin.qq.com/mp/appmsg/show?__biz=MjM5NTY3NjAyMg==&appmsgid=10000022&itemidx=1&sign=4015ca2f093456d0b51a4e7b5663a242#wechat_redirect",
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
                    "name": "期末成绩",
                    "key": "score",
                    "sub_button": []
                },
                {
                    "type": "view",
                    "name": "四六级成绩",
                    "url": "http://115.159.64.43/CETQuery/",
                    "sub_button": []
                },
                {
                    "type": "view",
                    "name": "图书馆找书",
                    "url": "http://61.142.33.201:8090/sms/opac/search/showiphoneSearch.action",
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
                    "type": "view",
                    "name": "玩小游戏",
                    "url": "http://autobox.meiriq.com/list/302da1ab?from=gxgkcat",
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
