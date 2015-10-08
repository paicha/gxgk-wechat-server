#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import random
from .. import app

default_answer = ['么么哒', '说啥呢……', '叫我干嘛', '纳尼……', '=。=']


def bad_word_filter(answer):
    for word in ['微', '胸', '屌', '插', '叼', '操', '草', '舔',
                 '骚', '逼', '淫', '鸡巴', '嫖', '干你', '你妈',
                 '你妹', '越大声', '夹紧', '上床', '搜索', '不要停',
                 '淘宝', '扣扣']:
        if word in answer:
            return True
            break


def chat(text):
    url = 'http://api.simsimi.com/request.p'
    payload = {'key': app.config['SIMSIMI_KEY'],
               'text': text, 'lc': 'ch', 'ft': '1.0'}
    try:
        # 由于 API 的延迟过高，使用代理请求
        r = requests.get(url, params=payload, timeout=3,
                         proxies=app.config['HTTP_PROXIES'])
        answer = r.json()['response'].encode('utf-8')
    except Exception, e:
        app.logger.warning(u"simsimi 请求或解析失败: %s, text: %s" % (e, text))
        return random.choice(default_answer)
    else:
        # 过滤特殊关键词
        if bad_word_filter(answer):
            return random.choice(default_answer)
        else:
            if '鸡' in answer or 'simsimi' in answer:
                answer = answer.replace('小黄鸡', '小喵')
                answer = answer.replace('鸡', '喵')
                answer = answer.replace('simsimi', '小喵')
            return answer
