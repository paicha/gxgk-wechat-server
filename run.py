#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main import app

if __name__ == "__main__":
    app.debug = app.config['DEBUG']
    app.run()
