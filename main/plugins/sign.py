#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime
from ..models import get_sign_info, update_sign_info


def daily_sign(openid):
    # 统一使用毫秒
    current_milli_time = int(round(time.time() * 1000))
    current_hour = int(datetime.fromtimestamp(
        current_milli_time / 1000).strftime('%H'))

    if current_hour < 6:
        return None
    else:
        sign_info = get_sign_info(openid)
        # 读取上次签到时间戳
        last_sign_time = sign_info["lastsigntime"]
        # 今日凌晨的时间戳
        today_dt = datetime.fromtimestamp(
            current_milli_time / 1000).strftime('%Y-%m-%d')
        today_timestamp = int(round(time.mktime(
            datetime.strptime(today_dt, '%Y-%m-%d').timetuple()) * 1000))
        # 上次签到时间大于今日凌晨的时间戳，今日已经签到过
        if last_sign_time >= today_timestamp:
            # 返回签到信息
            totaldays = sign_info["totaldays"]
            keepdays = sign_info["keepdays"]
            today_sign_time = datetime.fromtimestamp(
                last_sign_time / 1000).strftime('%H:%M:%S')
            return {
                "first": {
                    "value": "今天已经签到过啦！"
                },
                "keyword1": {
                    "value": "每日签到"
                },
                "keyword2": {
                    "value": today_sign_time
                },
                "remark": {
                    "value": "累计签到：%s 天\n连续签到：%s 天\n\n今天广科第 %s 个签到！\n\n继续保持噢~" % (totaldays, keepdays, 1)
                }
            }
        else:
            # 更新签到，上次签到时间大于昨日凌晨的时间戳，续签
            yesterday_timestamp = today_timestamp - 86400 * 1000
            if last_sign_time == 0 or last_sign_time >= yesterday_timestamp:
                sign_info["keepdays"] += 1
            else:
                sign_info["keepdays"] = 1
            update_sign_info(openid, current_milli_time,
                             sign_info["totaldays"] + 1,
                             sign_info["keepdays"])
            today_sign_time = datetime.fromtimestamp(
                current_milli_time / 1000).strftime('%H:%M:%S')
            return {
                "first": {
                    "value": "签到成功！"
                },
                "keyword1": {
                    "value": "每日签到"
                },
                "keyword2": {
                    "value": today_sign_time
                },
                "remark": {
                    "value": "累计签到：%s 天\n连续签到：%s 天\n\n今天广科第 %s 个签到！\n\n继续保持噢~" % (sign_info["totaldays"] + 1, sign_info["keepdays"], 1)
                }
            }
