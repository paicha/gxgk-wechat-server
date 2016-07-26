#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup, SoupStrainer
import ast
import time
from .. import app, redis, celery
from ..models import set_user_student_info, set_user_realname_and_classname
from ..utils import AESCipher
from . import wechat_custom


@celery.task
def get_info(openid, studentid, studentpwd, check_login=False):
    # 优先读取缓存的成绩
    redis_prefix = "wechat:user:score:"
    redis_auth_prefix = "wechat:user:auth:score:"
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
        login_url = app.config['JW_LOGIN_URL']
        score_url = app.config['JW_SCORE_URL']
        try:
            res = login(studentid, studentpwd, login_url, session, proxy)
        except Exception, e:
            app.logger.warning(u'外网查询出错：%s' % e)
            # 外网查询超时，切换内网代理查询
            proxy = True
            login_url = app.config['JW_LOGIN_URL_LAN']
            score_url = app.config['JW_SCORE_URL_LAN']
            session.headers.update({'Referer': login_url})
            try:
                res = login(studentid, studentpwd, login_url, session, proxy)
            except Exception, e:
                app.logger.warning(u'内网查询出错：%s' % e)
                res = None

        # 登录成功之后，教务系统会返回 302 跳转
        if not res:
            if check_login:
                errmsg = u"教务系统连接超时，请稍后重试"
                redis.set(redis_auth_prefix + openid, errmsg, 10)
            else:
                content = u"教务系统连接超时\n\n请稍后重试"
                wechat_custom.send_text(openid, content)
        elif res.status_code == 200 and 'alert' in res.text:
            if check_login:
                errmsg = u"用户名或密码不正确"
                redis.set(redis_auth_prefix + openid, errmsg, 10)
            else:
                url = app.config['HOST_URL'] + '/auth-score/' + openid
                content = u'用户名或密码不正确\n\n' +\
                    u'<a href="%s">点这里重新绑定学号</a>' % url +\
                    u'\n\n绑定后重试操作即可'
                wechat_custom.send_text(openid, content)
        else:
            # 查询学习成绩
            try:
                res = score_page(studentid, score_url, session, proxy)
                # 解析 HTML 内容
                soup = BeautifulSoup(res.text, "html.parser")
                rows = soup.find(id='Datagrid1').find_all('tr')
            except Exception, e:
                app.logger.warning(u'登录成功，但是在校成绩查询或解析出错：%s,%s' % (
                    e, score_url))
                if check_login:
                    errmsg = u"教务系统连接超时，请稍后重试"
                    redis.set(redis_auth_prefix + openid, errmsg, 10)
                else:
                    content = u"学校的教务系统连接超时\n\n请稍后重试"
                    wechat_custom.send_text(openid, content)
            else:
                school_year = app.config['SCHOOL_YEAR']
                school_term = app.config['SCHOOL_TERM']
                # 提取当前学期的成绩
                content = u''
                score_info = []
                for row in rows:
                    cells = row.find_all("td")
                    year = cells[0].get_text()
                    term = cells[1].get_text()
                    if year == school_year and term == school_term:
                        lesson_name = cells[3].get_text()
                        score = cells[8].get_text()
                        # 组装文本格式数据回复用户
                        content = content + u'\n\n课程名称：%s\n考试成绩：%s' % (
                            lesson_name, score)
                        # 组装数组格式的数据备用
                        score_info.append({"lesson_name": lesson_name,
                                           "score": score})
                        # 有其他成绩内容则输出
                        makeup_score = cells[10].get_text()
                        retake_score = cells[11].get_text()
                        if makeup_score != u'\xa0':
                            content = content + u'\n补考成绩：%s' % makeup_score
                        if retake_score != u'\xa0':
                            content = content + u'\n重修成绩：%s' % retake_score
                # 保存用户真实姓名和所在班级信息
                realname = soup.find(id='Label5').get_text()[3:]
                classname = soup.find(id='Label8').get_text()[4:]
                set_user_realname_and_classname(openid, realname, classname)
                # 查询不到成绩
                if not content:
                    content = u'抱歉，没查询到结果\n可能还没公布成绩\n请稍候查询'
                    wechat_custom.send_text(openid, content)
                else:
                    url = app.config['HOST_URL'] + '/score-report/' + openid
                    data = [{
                        'title': u'%s 期末成绩' % realname
                    }, {
                        'title': u'【%s学年第%s学期】%s' % (school_year, school_term, content),
                        'url': url
                    }, {
                        'title': u'点击这里：分享成绩单到朋友圈',
                        'url': url
                    }]
                    # 缓存结果 1 小时
                    redis.set(redis_prefix + openid, data, 3600)
                    # 发送微信
                    wechat_custom.send_news(openid, data)
                    # 更新缓存成绩，用于 Web 展示，不设置过期时间
                    redis.hmset('wechat:user:scoreforweb:' + openid, {
                        "real_name": realname,
                        "school_year": school_year,
                        "school_term": school_term,
                        "score_info": score_info,
                        "update_time": time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                # 账号密码保存数据库
                if check_login:
                    # 加密密码
                    cipher = AESCipher(app.config['PASSWORD_SECRET_KEY'])
                    studentpwd = cipher.encrypt(studentpwd)
                    set_user_student_info(openid, studentid, studentpwd)
                    redis.set(redis_auth_prefix + openid, 'ok', 10)


def login(studentid, studentpwd, url, session, proxy):
    """登录获取 cookie"""
    # 先获取 VIEWSTATE
    if not proxy:
        pre_login = session.get(url, allow_redirects=False, timeout=5)
    else:
        pre_login = session.get(url, allow_redirects=False, timeout=5,
                                proxies=app.config['SCHOOL_LAN_PROXIES'])
    pre_login.raise_for_status()
    pre_login_soup = BeautifulSoup(pre_login.text, "html.parser",
                                   parse_only=SoupStrainer("input"))
    login_view_state = pre_login_soup.find(
        attrs={"name": "__VIEWSTATE"})['value']
    # 登录
    payload = {
        '__VIEWSTATE': login_view_state,
        'TextBox1': studentid,
        'TextBox2': studentpwd,
        'RadioButtonList1': u'学生',
        'Button1': u' 登 录 '
    }
    if not proxy:
        res = session.post(url, data=payload, allow_redirects=False, timeout=5)
    else:
        res = session.post(url, data=payload, allow_redirects=False, timeout=5,
                           proxies=app.config['SCHOOL_LAN_PROXIES'])
    return res


def score_page(studentid, url, session, proxy):
    """在校成绩页面"""
    url = url + studentid
    # 先获取查询成绩需要的 VIEWSTATE
    if not proxy:
        pre_score = session.get(url, allow_redirects=False, timeout=5)
    else:
        pre_score = session.get(url, allow_redirects=False, timeout=5,
                                proxies=app.config['SCHOOL_LAN_PROXIES'])
    pre_score_soup = BeautifulSoup(
        pre_score.text, "html.parser", parse_only=SoupStrainer("input"))
    score_view_state = pre_score_soup.find(
        attrs={"name": "__VIEWSTATE"})['value']
    # 查询成绩
    payload = {
        '__VIEWSTATE': score_view_state,
        'Button2': u'在校学习成绩查询',
        'ddlXN': '',
        'ddlXQ': ''
    }
    if not proxy:
        score_res = session.post(url, data=payload, allow_redirects=False,
                                 timeout=5)
    else:
        score_res = session.post(url, data=payload, allow_redirects=False,
                                 proxies=app.config['SCHOOL_LAN_PROXIES'],
                                 timeout=5)
    return score_res
