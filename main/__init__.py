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

# 初始化微信 SDK
access_token = redis.get("wechat:access_token")
access_token_expires_at = redis.get("wechat:access_token_expires_at")
if access_token_expires_at:
    access_token_expires_at = int(access_token_expires_at)
wechat = WechatBasic(appid=app.config['APP_ID'],
                     access_token=access_token,
                     access_token_expires_at=access_token_expires_at,
                     appsecret=app.config['APP_SECRET'],
                     token=app.config['TOKEN'])

# 路由
from .routes import *
# 定时任务
from .plugins.cron import *
