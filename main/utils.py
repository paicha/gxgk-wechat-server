#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from flask import request, redirect
import time
from . import app, wechat


current_milli_time = lambda: int(round(time.time() * 1000))


def check_signature(func):
    """
    微信签名验证
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')

        if not wechat.check_signature(signature=signature,
                                      timestamp=timestamp,
                                      nonce=nonce):
            if request.method == 'POST':
                return "signature failed"
            else:
                return redirect(app.config['MAIN_URL'])

        return func(*args, **kwargs)

    return decorated_function
