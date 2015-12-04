#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup, SoupStrainer
from .. import app, celery
from ..models import set_user_library_info
from ..utils import AESCipher
import wechat_custom


@celery.task
def get_borrowing_record(openid, libraryid, librarypwd, check_login=False):
    """查询借书记录"""
    session = requests.Session()
    try:
        login_res = login(session, libraryid, librarypwd)
    except Exception, e:
        app.logger.warning(u'图书馆登录失败：%s' % e)
        if check_login:
            return u'图书馆网站连接超时'
        else:
            content = u"图书馆网站连接超时\n\n请稍候重试"
            wechat_custom.send_text(openid, content)
    else:
        if login_res != 'ok':
            if check_login:
                return login_res
            else:
                auth_url = app.config['HOST_URL'] + '/auth-library/' + openid
                content = u'借书卡号或密码错误\n\n<a href="%s">点这里重新绑定借书卡</a>\n\n绑定后重试操作即可' % auth_url
                wechat_custom.send_text(openid, content)
        else:
            record_url = app.config['LIBRARY_RECORD_URL']
            try:
                record = session.get(record_url, timeout=7)
            except Exception, e:
                app.logger.warning(u'图书馆登录成功，但是查询借书失败：%s' % e)
                if check_login:
                    return u'图书馆网站连接超时'
                else:
                    content = u"图书馆网站连接超时\n\n请稍候重试"
                    wechat_custom.send_text(openid, content)
            else:
                record.encoding = 'gbk'
                soup = BeautifulSoup(record.text, "html.parser",
                                     parse_only=SoupStrainer("table"))
                rows = soup.find_all('tr')[1:]
                if len(rows) == 0:
                    content = u'你现在没有在借图书\n\n<a href="http://61.142.33.201:8090/sms/opac/search/showiphoneSearch.action">搜索图书馆书籍：点击这里</a>'
                    wechat_custom.send_text(openid, content)
                else:
                    content = u''
                    for row in rows:
                        cells = row.find_all("td")
                        book_name = cells[2].get_text()
                        book_code = cells[3].get_text()
                        book_type = cells[4].get_text()
                        return_book = cells[6].get_text()
                        content = content + \
                            u'图书题名：%s\n图书条码：%s\n典藏部门：%s\n还书日期：%s\n\n' % (
                                book_name, book_code, book_type, return_book)
                    data = [{
                        'title': u'当前在借图书：%d本' % len(rows)
                    }, {
                        'title': content + u"回复“续借”将7天内到期的书籍续借30天\n注意续借天数是从续借当天开始计算"
                    }]
                    wechat_custom.send_news(openid, data)
                # 账号密码保存数据库
                if check_login:
                    # 加密密码
                    cipher = AESCipher(app.config['PASSWORD_SECRET_KEY'])
                    librarypwd = cipher.encrypt(librarypwd)
                    set_user_library_info(openid, libraryid, librarypwd)
                    return 'ok'


def login(session, libraryid, librarypwd):
    """登录"""
    login_url = app.config['LIBRARY_LOGIN_URL']
    payload = {
        'login_type': 'barcode',
        'barcode': libraryid,
        'password': librarypwd,
        '_': ''
    }
    login = session.post(login_url, data=payload, timeout=7)
    return login.text
