#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from .. import app, celery, redis
from bs4 import BeautifulSoup
import urlparse
import ast
from . import wechat_custom


@celery.task
def get(openid):
    """获取最新的学院新闻"""
    # 优先读取缓存
    redis_key = 'wechat:school_news'
    news_cache = redis.get(redis_key)
    if news_cache:
        content = ast.literal_eval(news_cache)
        wechat_custom.send_news(openid, content)
    else:
        url = app.config['SCHOOL_NEWS_URL']
        try:
            res = requests.get(url, timeout=6)
        except Exception, e:
            app.logger.warning(u'学院官网连接超时出错：%s' % e)
            content = u'学院官网连接超时\n请稍后重试'
            wechat_custom.send_text(openid, content)
        else:
            soup = BeautifulSoup(res.text, "html.parser")
            rows = soup.find(id='listbody').find_all('a')[:7]  # 图文推送条数
            content = []
            for row in rows:
                title = row.text
                link = urlparse.urljoin(url, row['href'])
                data = {
                    "title": title,
                    "url": link
                }
                content.append(data)
            # 缓存结果 12 小时
            redis.set(redis_key, content, 3600 * 12)
            wechat_custom.send_news(openid, content)
