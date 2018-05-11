# coding:utf-8

import logging
from . import api


@api.route('/index')
def index():
    logging.error("err msg")
    logging.warn("warn msg")
    logging.info("info msg")
    logging.debug("debug msg")

    return 'index page ihome_py2'
