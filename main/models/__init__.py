#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
from .. import app

db = SQLAlchemy(app)
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

from .auth import *
from .express import *
from .sign import *
from .user import *
