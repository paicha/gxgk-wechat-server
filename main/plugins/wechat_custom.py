#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from ..utils import get_wechat_access_token
from .. import app


def send_text(openid, content):
    """组装文本回复数据"""
    data = {
        "touser": openid,
        "msgtype": "text",
        "text":
        {
            "content": content
        }
    }
    return send_message(data)


def send_news(openid, content):
    """组装图文回复数据"""
    data = {
        "touser": openid,
        "msgtype": "news",
        "news": {
            "articles": content
        }
    }
    return send_message(data)


def send_message(data):
    """
    使用客服接口主动推送消息
    """
    url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?" + \
        "access_token=%s" % get_wechat_access_token()
    try:
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        r = requests.post(url, data=payload)
        response = r.json()
    except Exception, e:
        app.logger.warning(u"客服接口推送信息失败: %s, %s" % (e, payload))
    else:
        if response["errmsg"] != 'ok':
            app.logger.warning(u"客服接口推送信息失败信息: %s, %s"
                               % (response["errmsg"], data))
        return None
