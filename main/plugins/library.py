#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup, SoupStrainer
from .. import app, celery, redis
from ..models import set_user_library_info
from ..utils import AESCipher
from . import wechat_custom
import time
from datetime import datetime
import re


@celery.task
def borrowing_record(openid, libraryid, librarypwd,
                     check_login=False, renew=False):
    """查询借书记录，根据参数做登录验证或续借书籍"""
    redis_auth_prefix = "wechat:user:auth:library:"
    session = requests.Session()
    proxy = False
    login_url = app.config['LIBRARY_LOGIN_URL']
    record_url = app.config['LIBRARY_RECORD_URL']
    # 登录获取 cookie
    try:
        login_res = login(session, libraryid, librarypwd, login_url, proxy)
    except Exception, e:
        app.logger.warning(u'外网图书馆登录失败：%s' % e)
        # 外网查询超时，切换内网代理查询
        proxy = True
        login_url = app.config['LIBRARY_LOGIN_URL_LAN']
        record_url = app.config['LIBRARY_RECORD_URL_LAN']
        try:
            login_res = login(session, libraryid, librarypwd, login_url, proxy)
        except Exception, e:
            app.logger.warning(u'图书馆内网查询出错：%s' % e)
            login_res = None

    # 判断登录结果
    if not login_res or login_res.status_code != 200:
        if check_login:
            errmsg = u'图书馆网站连接超时'
            redis.set(redis_auth_prefix + openid, errmsg, 10)
        else:
            content = u"图书馆网站连接超时\n\n请稍候重试"
            wechat_custom.send_text(openid, content)
    elif login_res.status_code == 200 and login_res.text != 'ok':
        if check_login:
            errmsg = login_res.text
            redis.set(redis_auth_prefix + openid, errmsg, 10)
        else:
            auth_url = app.config['HOST_URL'] + '/auth-library/' + openid
            content = u'借书卡号或密码错误\n\n<a href="%s">点这里重新绑定借书卡</a>\n\n绑定后重试操作即可' % auth_url
            wechat_custom.send_text(openid, content)
    else:
        # 登录成功后，获取初始的借书记录
        try:
            record = get_record(session, record_url, proxy)
            record.encoding = 'gbk'
        except Exception, e:
            app.logger.warning(u'图书馆登录成功，但是查询借书失败：%s' % e)
            if check_login:
                errmsg = u'图书馆网站连接超时'
                redis.set(redis_auth_prefix + openid, errmsg, 10)
            else:
                content = u"图书馆网站连接超时\n\n请稍候重试"
                wechat_custom.send_text(openid, content)
        else:
            rows = get_html_tr_list(record)
            if len(rows) == 0:
                content = u'你当前无在借图书\n\n<a href="http://61.142.33.201:8090/sms/opac/search/showiphoneSearch.action">搜索图书馆书籍：点击这里</a>'
                wechat_custom.send_text(openid, content)
            else:
                # 续借书籍
                if renew:
                    renew_books(openid, session, record.text, rows,
                                record_url, proxy)
                else:
                    send_record(openid, rows)
            # 账号密码保存数据库
            if check_login:
                # 加密密码
                cipher = AESCipher(app.config['PASSWORD_SECRET_KEY'])
                librarypwd = cipher.encrypt(librarypwd)
                set_user_library_info(openid, libraryid, librarypwd)
                redis.set(redis_auth_prefix + openid, 'ok', 10)


def login(session, libraryid, librarypwd, url, proxy):
    """登录"""
    payload = {
        'login_type': 'barcode',
        'barcode': libraryid,
        'password': librarypwd,
        '_': ''
    }
    if not proxy:
        login = session.post(url, data=payload, timeout=5)
    else:
        login = session.post(url, data=payload, timeout=5,
                             proxies=app.config['SCHOOL_LAN_PROXIES'])
    login.raise_for_status()
    return login


def get_record(session, url, proxy):
    """获取借书记录"""
    if not proxy:
        res = session.post(url, timeout=5)
    else:
        res = session.post(url, timeout=5,
                           proxies=app.config['SCHOOL_LAN_PROXIES'])
    return res


def renew_books(openid, session, html, rows, url, proxy):
    """续借7天内过期的书籍"""
    # 续借书籍需要 post 的数据
    department_id = re.findall('Renew\(\'.*\',\'(.*)\',', html)
    library_id = re.findall('Renew\(\'.*\',\'.*\',\'(.*)\'', html)

    renew_books_times = 0
    outdate_books_times = 0
    for index, row in enumerate(rows):
        cells = row.find_all("td")
        # 去除空格，转换为时间戳
        deadline = cells[6].get_text().replace(u'\xa0', '')
        deadline = time.mktime(
            datetime.strptime(deadline, '%Y/%m/%d').timetuple()) + 24 * 3600
        now = time.time()
        if deadline >= now and deadline - now < 7 * 24 * 3600:
            # 有效期小于 7 天，续期
            book_barcode = cells[3].get_text().replace(u'\xa0', '')
            payload = {
                'action': 'Renew',
                'book_barcode': book_barcode,
                'department_id': department_id[index],
                'library_id': library_id[index]
            }
            if not proxy:
                res = session.post(url, data=payload, timeout=5)
            else:
                res = session.post(url, data=payload, timeout=5,
                                   proxies=app.config['SCHOOL_LAN_PROXIES'])
            renew_books_times += 1
        elif deadline < now:
            outdate_books_times += 1

    if renew_books_times == 0 and outdate_books_times == 0:
        # 全部书籍有效期大于 7 天
        content_end = u'还书期限大于7天，目前不需要续借'
    elif renew_books_times == 0 and outdate_books_times == len(rows):
        # 全部书籍都过期
        content_end = u'续借失败！\n全部书籍逾期未还\n请尽快到图书馆还书'
    elif renew_books_times == 0 and outdate_books_times > 0:
        # 无需要续期书籍，而且部分书籍过期
        content_end = u'部分书籍逾期未还\n请尽快到图书馆还书\n其他图书目前不需要续借'
    elif renew_books_times > 0:
        res.encoding = 'gbk'
        rows = get_html_tr_list(res)
        if outdate_books_times > 0:
            # 续期至少一本书籍，而且有过期书籍
            content_end = u'续借成功！\n部分书籍逾期未还\n请尽快到图书馆还书'
        else:
            # 续期至少一本书籍，而且无过期书籍
            content_end = u'续借成功！\n\n每本书只能续借一次'

    # 发送最新的借书记录
    send_record(openid, rows, content_end=content_end)


def send_record(openid, rows, content_end=None):
    """解析借书记录，发送给用户"""
    if not content_end:
        content_end = u'回复“续借”将 7 天内到期的书籍续借 30 天\n' +\
            u'续借天数是从续借当天开始计算'
    content = u''
    for row in rows:
        cells = row.find_all("td")
        book_name = cells[2].get_text()
        book_type = cells[4].get_text()
        book_state = cells[5].get_text()
        return_time = cells[6].get_text()
        content = content + \
            u'图书题名：%s\n典藏部门：%s\n流通状态：%s\n还书日期：%s\n\n' % (
                book_name, book_type, book_state, return_time)
    data = [{
        'title': u'当前在借图书：%d本' % len(rows)
    }, {
        'title': content + content_end
    }]
    wechat_custom.send_news(openid, data)


def get_html_tr_list(res):
    """解析HTML获取借书表格每行的数据"""
    # 修正不规范的 HTML
    html = res.text.replace('TR', 'tr').replace('<td width=7></td></tr>', '')
    soup = BeautifulSoup(html, "html.parser", parse_only=SoupStrainer("table"))
    rows = soup.find_all('tr')[1:]  # 第一行是列名，去掉
    return rows


def time_to_return_books(openid, libraryid, librarypwd):
    """判断是否有图书准备过期"""
    session = requests.Session()
    login_url = app.config['LIBRARY_LOGIN_URL']
    record_url = app.config['LIBRARY_RECORD_URL']
    # 登录获取 cookie
    login_res = login(session, libraryid, librarypwd, login_url, False)
    # 判断登录结果
    if login_res.status_code == 200 and login_res.text == 'ok':
        record = get_record(session, record_url, False)
        record.encoding = 'gbk'
        rows = get_html_tr_list(record)
        if len(rows) > 0:
            for row in rows:
                cells = row.find_all("td")
                # 去除空格，转换为时间戳
                deadline = cells[6].get_text().replace(u'\xa0', '')
                deadline = time.mktime(
                    datetime.strptime(deadline, '%Y/%m/%d').timetuple()) + 24 * 3600
                now = time.time()
                # 有效期小于 1 天
                if deadline >= now and deadline - now < 1 * 24 * 3600:
                    content_end = u"你有图书明天就过期了\n请续期或尽快到图书馆还书"
                    send_record(openid, rows, content_end)
                    break
