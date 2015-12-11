#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import app, celery
import hashlib
import hmac
import time
import requests
from . import wechat_custom


@celery.task
def get(openid):
    """获取天气与空气质量预报"""
    content = []
    current_hour = time.strftime('%H')
    try:
        pm_25_info = get_pm2_5_info()
    except Exception, e:
        app.logger.warning(u'PM2.5 API 超时出错：%s' % e)
    else:
        title_aqi = u'空气质量等级：%s\n%s点的平均PM2.5：%s' % (
            pm_25_info[0]['quality'], current_hour, pm_25_info[0]['pm2_5'])
        content.append({"title": title_aqi})
    try:
        weather_info = get_weather_info()
    except Exception, e:
        app.logger.warning(u'天气 API 超时出错：%s' % e)
        content = u"天气查询超时\n请稍后重试"
        wechat_custom.send_text(openid, content)
    else:
        for index, data in enumerate(weather_info):
            title_weather = u'%s  %s℃\n%s  %s ' % (
                day_of_week(offset=index),
                data['temp'],
                data['weather'],
                data['wind'])
            content.append({"title": title_weather, "picurl": data['img_url']})

        wechat_custom.send_news(openid, content)


def get_weather_info():
    """
    查询气象
    API 详情：http://openweather.weather.com.cn/Home/Help/Product.html
    气象图片下载：http://openweather.weather.com.cn/Home/Help/icon/iid/10.html
    """
    private_key = app.config['WEATHER_PRIVATE_KEY']
    appid = app.config['WEATHER_APPID']
    appid_six = appid[:6]
    areaid = '101281601'  # 东莞代号
    date = time.strftime('%Y%m%d%H%M')
    # 根据 API 文档生成请求 URL
    public_key = 'http://open.weather.com.cn/data/?' +\
        'areaid=%s&type=forecast_v&date=%s&appid=%s' % (areaid, date, appid)
    key = hmac.new(private_key, public_key, hashlib.sha1).digest().encode(
        'base64').rstrip()
    url = 'http://open.weather.com.cn/data/?' +\
        'areaid=%s&type=forecast_v&date=%s&appid=%s&key=%s' % (
            areaid, date, appid_six, key)
    res = requests.get(url, timeout=7)
    weather_info = res.json()['f']['f1']
    # 解析为可读数据
    img_url = "http://gxgk-wechat.b0.upaiyun.com/weather/day/%s.jpeg"
    data = []
    for weather in weather_info:
        # 到了晚上，当日白天的数据为空，所以使用晚上的数据
        if weather['fa'] == u'':
            temp = weather['fd']
            weather_code = weather['fb']
            wind_code = weather['ff']
        else:
            temp = weather['fc']
            weather_code = weather['fa']
            wind_code = weather['fe']
        data.append({
            "temp": temp,
            "weather": weather_code_to_text(weather_code),
            "wind": wind_code_to_text(wind_code),
            "img_url": img_url % weather_code
        })
    return data


def get_pm2_5_info():
    """
    空气质量
    API 详情：http://www.pm25.in/api_doc
    """
    url = 'http://www.pm25.in/api/querys/pm2_5.json?' +\
        'city=dongguan&token=%s&stations=no' % app.config['PM2_5_TOKEN']
    res = requests.get(url, timeout=7)
    return res.json()


def day_of_week(offset=0):
    """获取星期几"""
    day_of_week = int(time.strftime('%w')) + offset
    days = [u'周日', u'周一', u'周二', u'周三', u'周四', u'周五', u'周六',
            u'周日', u'周一']
    prefix = [u'今天', u'明天', u'后天']
    return prefix[offset] + days[day_of_week]


def weather_code_to_text(code):
    """转换天气代码为文字"""
    weather_list = [u'晴', u'多云', u'阴', u'阵雨', u'雷阵雨', u'雷阵雨伴有冰雹',
                    u'雨夹雪', u'小雨', u'中雨', u'大雨', u'暴雨', u'大暴雨',
                    u'特大暴雨', u'阵雪', u'小雪', u'中雪', u'大雪', u'暴雪', u'雾',
                    u'冻雨', u'沙尘暴', u'小到中雨', u'中到大雨', u'大到暴雨',
                    u'暴雨到大暴雨', u'大暴雨到特大暴雨', u'小到中雪', u'中到大雪',
                    u'大到暴雪', u'浮尘', u'扬沙', u'强沙尘暴', u'霾', u'无']
    return weather_list[int(code)]


def wind_code_to_text(code):
    """转换风向代码为文字"""
    wind_list = [u'微风', u'东北风', u'东风', u'东南风', u'南风', u'西南风',
                 u'西风', u'西北风', u'北风', u'旋转风']
    return wind_list[int(code)]
