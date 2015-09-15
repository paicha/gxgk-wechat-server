#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from redis import Redis
from wechat_sdk import WechatBasic

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

redis = Redis()
wechat = WechatBasic(appid=app.config['APP_ID'],
                     appsecret=app.config['APP_SECRET'],
                     token=app.config['TOKEN'])

from .routes import *
