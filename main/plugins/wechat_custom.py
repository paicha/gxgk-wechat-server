#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from ..utils import get_wechat_access_token, update_wechat_token
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


def send_music(openid, title, desc, music_url, thumb_media_id):
    """组装音乐回复数据"""
    data = {
        "touser": openid,
        "msgtype": "music",
        "music":
        {
            "title": title,
            "description": desc,
            "musicurl": music_url,
            "hqmusicurl": music_url,
            "thumb_media_id": thumb_media_id
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
        content = u"客服接口超时或解析失败，错误信息：%s\n提交内容：%s"
        app.logger.warning(content % (e, data))
    else:
        if response["errmsg"] != 'ok':
            content = u"客服推送失败: %s\n推送内容：%s"
            app.logger.warning(content % (response, data))
            if response["errcode"] == 40001:
                # access_token 失效，更新
                update_wechat_token()
                # 再发送
                send_message(data)
        return None
