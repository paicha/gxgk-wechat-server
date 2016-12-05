#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from .. import app, celery
from . import wechat_custom


@celery.task
def get_douban_fm(openid):
    """抓取豆瓣FM"""
    url = 'https://douban.fm/j/v2/playlist?' + \
        'app_name=radio_website&version=100&channel=0&type=n'
    try:
        r = requests.get(url, timeout=5)
        result = r.json()["song"][0]
        desc = result["artist"] + u'-建议WiFi下播放'
        music_url = result["url"]
        title = result["title"]
    except Exception, e:
        app.logger.warning(u"豆瓣FM请求或解析失败: %s" % e)
        context = u"网络繁忙，请稍候重试"
        wechat_custom.send_text(openid, context)
    else:
        # 客服接口推送音乐必须要有 thumb_media_id
        thumb_media_id = app.config["MUSIC_THUMB_MEDIA_ID"]
        wechat_custom.send_music(openid, title, desc, music_url, thumb_media_id)
