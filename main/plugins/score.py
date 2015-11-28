#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import ast
from .. import app, redis, celery
import wechat_custom


@celery.task
def get_info(openid, studentid, studentpwd, check_login=False):
    # 优先读取缓存的成绩
    redis_prefix = "wechat:user:score:"
    user_score_cache = redis.get(redis_prefix + openid)
    if user_score_cache and not check_login:
        content = ast.literal_eval(user_score_cache)
        wechat_custom.send_news(openid, content)
    else:
        # 建立会话
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; ' +
            'Windows NT 6.2; Trident/6.0)',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': app.config['JW_LOGIN_URL']})

        # 登录获取 cookie
        proxy = False
        score_url = app.config['GET_SCORE_URL']
        login_url = app.config['JW_LOGIN_URL']
        try:
            res = login(studentid, studentpwd, login_url, session, proxy)
        except Exception, e:
            app.logger.warning(u'外网查询出错：%s' % e)
            # 外网查询超时，切换内网代理查询
            proxy = True
            score_url = app.config['GET_SCORE_URL_LAN']
            login_url = app.config['JW_LOGIN_URL_LAN']
            try:
                res = login(studentid, studentpwd, login_url, session, proxy)
            except Exception, e:
                app.logger.warning(u'内网查询出错：%s' % e)
                res = None

        # 登录成功之后，教务系统会返回 302 跳转
        if not res:
            if check_login:
                return u"教务系统连接超时，请稍后重试"
            else:
                content = u"教务系统连接超时\n\n请稍后重试"
                wechat_custom.send_text(openid, content)
        elif res.status_code == 200 and 'alert' in res.text:
            if check_login:
                return u"用户名或密码不正确"
            else:
                url = app.config['HOST_URL'] + '/auth-score/' + openid
                content = u'用户名或密码不正确\n\n' +\
                    u'<a href="%s">点这里重新绑定学号</a>' % url +\
                    u'\n\n绑定后重试操作即可'
                wechat_custom.send_text(openid, content)
        else:
            # 请求在校成绩页面
            try:
                res = score_page(studentid, score_url, session, proxy)
            except Exception, e:
                app.logger.warning(u'登录成功，但是在校成绩查询出错：%s,%s' % (
                    e, score_url))
                if check_login:
                    return u"教务系统连接超时，请稍后重试"
                else:
                    content = u"学校的教务系统连接超时\n\n请稍后重试"
                    wechat_custom.send_text(openid, content)
            else:
                # 解析 HTML 内容
                soup = BeautifulSoup(res.text, "html.parser")
                rows = soup.find(id='Datagrid1').find_all('tr')
                name = soup.find(id='Label5').get_text()[3:]
                # 提取当前学期的成绩
                content = u''
                for row in rows:
                    cells = row.find_all("td")
                    school_year = cells[0].get_text()
                    school_term = cells[1].get_text()
                    if school_year == '2014-2015' and school_term == '2':
                        content = content + u'\n\n课程名称：%s\n考试成绩：%s' % (
                            cells[3].get_text(),
                            cells[8].get_text())
                        # 有其他成绩内容则输出
                        makeup_score = cells[10].get_text()
                        retake_score = cells[11].get_text()
                        if makeup_score != u'\xa0':
                            content = content + u'\n补考成绩：%s' % makeup_score
                        if retake_score != u'\xa0':
                            content = content + u'\n重修成绩：%s' % retake_score
                # 查询不到成绩
                if not content:
                    content = u'抱歉，没查询到成绩\n可能还没公布成绩\n请稍候查询'
                    wechat_custom.send_text(openid, content)
                else:
                    data = [{
                        'title': u'%s 期末成绩' % name
                    }, {
                        'title': u'【2014-2015学年第二学期】%s' % content
                    }]
                    # 缓存结果 30 分钟
                    redis.set(redis_prefix + openid, data, 60 * 30)
                    # 发送微信
                    wechat_custom.send_news(openid, data)
                # TODO 账号密码保存数据库
                if check_login:
                    return 'ok'


def login(studentid, studentpwd, url, session, proxy):
    """登录获取 cookie"""
    payload = app.config['LOGIN_VIEW_STATE'] +\
        '&TextBox1=%s&TextBox2=%s' % (studentid, studentpwd) +\
        '&RadioButtonList1=%D1%A7%C9%FA&Button1=+%B5%C7+%C2%BC+'
    if not proxy:
        res = session.post(url, data=payload, allow_redirects=False, timeout=7)
    else:
        res = session.post(url, data=payload, proxies=app.config['JW_PROXIES'],
                           allow_redirects=False, timeout=7)
    return res


def score_page(studentid, url, session, proxy):
    """在校成绩页面"""
    payload = app.config['SCORE_VIEW_STATE'] +\
        '&ddlXN=&ddlXQ=&Button2=%D4%DA%D0%A3%D1' +\
        '%A7%CF%B0%B3%C9%BC%A8%B2%E9%D1%AF'
    if not proxy:
        res = session.post(url + studentid, data=payload, allow_redirects=False,
                           timeout=7)
    else:
        res = session.post(url + studentid, data=payload, allow_redirects=False,
                           proxies=app.config['JW_PROXIES'], timeout=7)
    return res
