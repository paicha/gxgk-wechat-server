#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
from redis import Redis
from wechat_sdk import WechatBasic
from .plugins.tasks import make_celery

app = Flask(__name__, instance_relative_config=True)
# 加载配置
app.config.from_object('config')
app.config.from_pyfile('config.py')

# 队列
celery = make_celery(app)

# 记录日志
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
handler.setLevel(logging.WARNING)
app.logger.addHandler(handler)

# 初始第三方库
redis = Redis()
wechat = WechatBasic(appid=app.config['APP_ID'],
                     appsecret=app.config['APP_SECRET'],
                     token=app.config['TOKEN'])

from .routes import *
