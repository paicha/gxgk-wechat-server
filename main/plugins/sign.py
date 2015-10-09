#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime
from ..models import get_sign_info, update_sign_info, get_today_sign_ranklist, \
    get_sign_keepdays_ranklist


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
            # 排行榜信息
            ranklist_data = ranklist_and_user_rank(openid, today_timestamp)
            content = u"\n今天广科第 %s 个签到！"
            return {
                "template_data": {
                    "first": {
                        "value": "今天已经签到过啦！"
                    },
                    "keyword1": {
                        "value": today_sign_time
                    },
                    "keyword2": {
                        "value": keepdays
                    },
                    "keyword3": {
                        "value": totaldays
                    },
                    "remark": {
                        "value": content % ranklist_data['user_sign_rank']
                    }
                },
                "ranklist": ranklist_data['ranklist_content']}
        else:
            # 更新签到，上次签到时间大于昨日凌晨的时间戳，续签
            yesterday_timestamp = today_timestamp - 86400 * 1000
            if last_sign_time == 0 or last_sign_time >= yesterday_timestamp:
                sign_info["keepdays"] += 1
            else:
                sign_info["keepdays"] = 1
            # 写入今日签到信息
            update_sign_info(openid, current_milli_time,
                             sign_info["totaldays"] + 1,
                             sign_info["keepdays"])
            today_sign_time = datetime.fromtimestamp(
                current_milli_time / 1000).strftime('%H:%M:%S')
            # 获取最新的排行榜信息
            ranklist_data = ranklist_and_user_rank(openid, today_timestamp)
            content = u"\n今天广科第 %s 个签到！"
            return {
                "template_data": {
                    "first": {
                        "value": "签到成功！"
                    },
                    "keyword1": {
                        "value": today_sign_time
                    },
                    "keyword2": {
                        "value": sign_info["keepdays"]
                    },
                    "keyword3": {
                        "value": sign_info["totaldays"] + 1
                    },
                    "remark": {
                        "value":  content % ranklist_data['user_sign_rank']
                    }
                },
                "ranklist": ranklist_data['ranklist_content']}


def ranklist_and_user_rank(openid, today_timestamp):
    """今日签到排行榜、续签排行榜、用户排名"""

    # 查询今日签到排行榜
    ranklist = get_today_sign_ranklist(today_timestamp)
    # 计算今日签到排名
    sign_ranklist_content = u"【今日签到排行榜】"
    for (rank, ranklist) in enumerate(ranklist):
        ranklist[0].rank = rank + 1
        # 转换签到时间显示
        user_today_sign_time = datetime.fromtimestamp(
            ranklist[0].lastsigntime / 1000).strftime('%H:%M:%S')
        # 组合排行榜 Top 12 信息
        if ranklist[0].rank <= 12:
            sign_ranklist_content += u"\n%s. %s %s 连续%s天" % (
                ranklist[0].rank, ranklist[1], user_today_sign_time,
                ranklist[0].keepdays)
        # 该用户本次排名
        if ranklist[0].openid == openid:
            user_sign_rank = ranklist[0].rank

    # 续签排行榜
    keepdays_ranklist = get_sign_keepdays_ranklist()
    keepdays_ranklist_content = u"【学霸排行榜】"
    for (rank, keepdays_ranklist) in enumerate(keepdays_ranklist):
        keepdays_ranklist[0].rank = rank + 1
        keepdays_ranklist_content += u"\n%s. %s 连续签到%s天" % (
            keepdays_ranklist[0].rank,
            keepdays_ranklist[1],
            keepdays_ranklist[0].keepdays)

    return {
        "ranklist_content": sign_ranklist_content + "\n\n" + keepdays_ranklist_content,
        "user_sign_rank": user_sign_rank
    }
