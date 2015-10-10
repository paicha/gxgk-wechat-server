#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .. import celery


@celery.task(name='express.update')
def update_uncheck_express():
    pass
