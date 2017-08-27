This code is no longer being maintained.

项目已经不再维护，开源的目的更多是给新手一个参考 Demo

# gxgk-wechat-server
校园微信公众号后端，为在校学生提供一系列信息查询与便民服务。


**预览**：
!["预览"](http://i.v2ex.co/OA598S46.jpeg)

**主要功能**：

- [x] 期末成绩查询
    - [x] 手动查询
    - [x] 微信分享成绩单
- [x] 快递查询
    - [x] 单号查询
    - [x] 扫码查询
    - [x] 包裹动态，自动提醒
- [x] 校内图书馆
    - [x] 图书搜索
    - [x] 借书记录
    - [x] 一键续借
    - [x] 还书提醒
- [x] 签到排行榜
- [x] 机器人陪聊

**其他**：

- [x] 天气查询
- [x] 常用电话
- [x] 公交路线
- [x] 校历查询
- [x] 学校新闻
- [x] 四六级查询
- [x] 明信片查询
- [x] 随机音乐
- [x] 气象雷达
- [x] 网页游戏
- [x] 莞香广科论坛
- [x] 客服留言
- [x] 合作信息

补充说明：

- 依赖外部 API 的操作使用客服接口异步回复，需要通过微信认证
- 正方教务系统与图书馆查询均使用模拟登陆
- 字典、正则匹配关键词，避免过多的条件语句嵌套
- 场景状态，支持上下文回复
- 全局保存、刷新微信 access_token
- 关键词兼容繁体、全角空格
- 长文本的回复使用图文信息进行排版
- 前端 UI 使用 WeUI 统一风格

## 快速开始

安装 MySQL、Redis
```
略
```

安装依赖

```
pip install -r requirements.txt
```

创建配置文件
```
cp instance/config.example instance/config.py
vi instance/config.py
```

初始化数据库

```
# into Python shell
>>> from main.models import db
>>> db.create_all()
```

运行

```
python run.py
```

运行队列任务

```
celery -A main.celery worker --beat -l info
```

测试

```
这个开发者很懒，暂时没写下什么测试……
```

部署

```
# using gunicorn
pip install gunicorn

# run
gunicorn -w 3 run:app -p wechat.pid -b 127.0.0.1:8000 -D --log-level warning --error-logfile gunicorn-error.log

# reload
kill -HUP `cat wechat.pid`
```

## License
[MIT](LICENSE)
