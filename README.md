# gxgk-wechat-server
莞香广科微信公众号后端，为在校学生提供一系列信息查询与便民服务。

!["微信号 GXGKCAT"](http://gxgk-wechat.b0.upaiyun.com/qrcode_for_gh_637c9ac560fd_258.jpg)

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

## 快速开始

安装 MySQL、Redis
```
略
```

安装依赖

```
pip install -r requirements.txt
``` 

设置运行参数
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
gunicorn run:app -p wechat.pid -b 127.0.0.1:8000 -D

# reload
kill -HUP `cat wechat.pid`
```

## License
[MIT](LICENSE)
