#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = False
MAIN_URL = "http://bbs.gxgk.cc/wechat/"

WELCOME_TEXT = u"感谢关注莞香广科[愉快]\n我是广科助手小喵[调皮]\n\n"

COMMAND_TEXT = u"请回复以下关键词开始：\n——————————\n电话  图书馆\n\n成绩  四六级\n\n客服  签到\n\n音乐  游戏  雷达\n\n论坛\n\n快递  公交  天气\n\n校历  新闻  合作\n\n点击左下角切换菜单"

COMMAND_NOT_FOUND_TEXT = u"输入错误关键词了？\n关键词前后不需要空格\n\n"

HELP_TEXT = u"\n\n回复 “ ? ” 查看主菜单"

PHONE_NUMBER_TEXT = u"————办公————\n校园网 0769-86211959\n\n院办室 0769-86211800\n\n学生处 0769-86211913\n\n教务处 0769-86211915\n\n招生办 0769-86211555\n\n————外卖————\n 台湾卤肉饭\n 13546976798/666798\n 旺记烧鹅\n 15015411456/671456\n 南香木桶饭\n 18824345816/674707\n 捷报源\n 15913751122/681122\n 良记\n 13437413545/33270668\n 电白菜馆\n 0769-22989348/666795\n 云香云吞面\n 15913776088/616088\n 隆江猪脚饭\n 13538360169/660169\n 米修吧\n 15989925944/644446\n 辉记餐厅\n 13662707099/627099\n QQ城市餐厅\n 13428578250/668250\n 好友邻\n 13723510289/660289\n 潮兴饭店\n 13622660754/660754\n 沙县小吃\n 13537367224\n\n 味力果\n 13423403880/671234\n 美食美客\n 13763281883/69988\n 布维记\n 18929100900/63666\n 地下铁\n 13712428381/668381\n 茶品道\n 0769-28828443\n 潘多拉\n 18926840222"

LEAVE_A_MESSAGE_TEXT = u"Hi~这里是小喵~\n请听到喵一声之后留言\n\n喵~回复：m+内容\n如：m小喵是笨蛋"

WEATHER_RADAR_TEXT = u'<a href="http://www.dg121.com/tianqiziliao/donghua_yun_radar/radar.gif">东莞雷达回波</a>'

HTML5_GAMES_TEXT = u'<a href="http://autobox.meiriq.com/list/302da1ab">点击玩游戏</a>'

POSTCARD_TEXT = u'<a href="https://jinshuju.net/s/iBxE0L">明信片查询</a>'

CONTACT_US_TEXT = u"我们欢迎各类型的合作\n　\n请联系：weixin@gxgk.cc\nQQ：723144293"

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
                    "type": "click",
                    "name": "成绩查询",
                    "key": "score",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "快递查询",
                    "key": "express",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "常用电话",
                    "key": "phone_number",
                    "sub_button": []
                },
                {
                    "type": "view",
                    "name": "明信片查询",
                    "url": "https://jinshuju.net/s/iBxE0L",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "图书馆找书",
                    "key": "search_books",
                    "sub_button": []
                }
            ]
        },
        {
            "name": "广科社区",
            "sub_button": [
                {
                    "type": "view",
                    "name": "微信群聊",
                    "url": "http://quan.qgc.qq.com/164406354",
                    "sub_button": []
                },
                {
                    "type": "view",
                    "name": "广科论坛",
                    "url": "http://wsq.discuz.qq.com/?siteid=264557099",
                    "sub_button": []
                },
                {
                    "type": "view",
                    "name": "上网客户端",
                    "url": "http://www.gxgk.cc/",
                    "sub_button": []
                }
            ]
        },
        {
            "name": "ฅ'ω'ฅ",
            "sub_button": [
                {
                    "type": "click",
                    "name": "小喵陪聊",
                    "key": "chat_robot",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "每日签到",
                    "key": "qiandao",
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
