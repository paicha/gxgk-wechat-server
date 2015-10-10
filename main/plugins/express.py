#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from .. import app
from .. import celery
import wechat_custom
from ..models import set_express_num


@celery.task
def get_tracking_info(openid, num):
    """根据单号查询快递物流"""

    web_url = "http://m.kuaidi100.com/result.jsp?from=weixin&nu=%s" % num
    get_com_url = 'http://www.kuaidi100.com/autonumber/autoComNum?text=%s' % num
    try:
        # 获取快递公司代号
        com_code_res = requests.get(get_com_url, timeout=2)
        com_code = com_code_res.json()["auto"][0]["comCode"]
        # 查询物流
        get_info_url = 'http://www.kuaidi100.com/query?type=%s&postid=%s' % (
            com_code, num)
        info_res = requests.get(get_info_url, timeout=3)
        tracking_info = info_res.json()
    except Exception, e:
        app.logger.warning(u"快递公司代号请求或解析失败: %s, num: %s" % (e, num))
        context = u'网络繁忙或者单号有误\n请检查单号是否正确\n\n单号无误请点击：' + \
            u'<a href="%s">重新查询</a>' % web_url
        wechat_custom.send_text(openid, context)
    else:
        if tracking_info["message"] == "ok":
            des = u'%s： %s\n更新时间：%s\n\n最新状态：%s\n\n有新动态小喵会通知你哦！\n点击查看详情' % (
                com_code_to_text(com_code), num,
                tracking_info["data"][0]["time"],
                tracking_info["data"][0]["context"])
            context = [{
                'title': u'快递最新物流',
                'url': web_url
            }, {
                'title': des,
                'url': web_url
            }]
            wechat_custom.send_news(openid, context)
            # 写入数据库
            set_express_num(openid, num, com_code,
                            tracking_info["data"][0]["time"],
                            tracking_info["ischeck"])
        elif tracking_info["status"] == '201':
            context = u'单号不存在或者已经过期 \n\n' + \
                u'点击：<a href="%s">重新查询</a>' % web_url
            wechat_custom.send_text(openid, context)
        else:
            context = u'%s \n\n点击：<a href="%s">重新查询</a>' % \
                (tracking_info["message"], web_url)
            wechat_custom.send_text(openid, context)


def com_code_to_text(com_code):
    """转换快递公司名称"""
    com_list = {"zhongtong": u"中通速递",
                "shentong": u"申通快递",
                "yuantong": u"圆通速递",
                "shunfeng": u"顺丰速运",
                "ems": u"EMS",
                "yunda": u"韵达快递",
                "rufengda": u"如风达",
                "huitongkuaidi": u"汇通快运",
                "tiantian": u"天天快递",
                "debangwuliu": u"德邦物流",
                "zhaijisong": u"宅急送"}
    try:
        text = com_list[com_code]
    except KeyError:
        return "快递"
    else:
        return text
