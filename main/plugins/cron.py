#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from .. import celery
from ..models import get_uncheck_express
from express import get_tracking_info


@celery.task(name='express.update')
def update_uncheck_express():
    """更新未签收的快递动态"""
    data = get_uncheck_express()
    if not data:
        return None
    else:
        for express in data:
            get_tracking_info.delay(
                express.openid,
                express.num,
                express.comcode,
                from_user_input=False)


@celery.task(name='access_token.update')
def update_access_token():
    """定时更新微信 access_token"""
    requests.get('http://127.0.0.1:5000/update_access_token')
