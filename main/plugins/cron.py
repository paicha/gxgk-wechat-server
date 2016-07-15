#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import celery, app
from ..models import get_all_uncheck_express, get_all_auth_info
from ..utils import AESCipher, update_wechat_token
from .express import get_tracking_info
from .library import time_to_return_books
import time
from .state import get_user_last_interact_time


@celery.task(name='express.update')
def update_uncheck_express():
    """更新未签收的快递动态"""
    data = get_all_uncheck_express()
    if not data:
        return None
    else:
        for express in data:
            get_tracking_info.delay(
                express.openid,
                express.num,
                express.comcode,
                from_user_input=False)


@celery.task(name='library.return_books')
def remind_return_books():
    """定时查询提醒还书"""
    data = get_all_auth_info()
    for user in data:
        timeout = time.time() - int(get_user_last_interact_time(user.openid))
        # 绑定了图书馆借书卡，并且在可主动回复时间内
        if user.libraryid and user.librarypwd and timeout <= 48 * 3600 * 0.99:
            # 解密密码
            cipher = AESCipher(app.config['PASSWORD_SECRET_KEY'])
            librarypwd = cipher.decrypt(user.librarypwd)
            try:
                time_to_return_books(user.openid, user.libraryid, librarypwd)
            except Exception, e:
                app.logger.warning(u'还书提醒任务出错：%s' % e)
            time.sleep(10)


@celery.task(name='access_token.update')
def update_access_token():
    """定时更新微信 access_token，写入缓存"""
    update_wechat_token()
