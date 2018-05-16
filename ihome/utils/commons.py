# coding:utf-8

from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from ihome.utils.response_code import RET
from functools import wraps


class RegexConverter(BaseConverter):
    """自定义的接收正则表达式的转换器"""

    def __init__(self, url_map, regex):
        """regex是在路由中填写的正则表达式"""
        super(RegexConverter, self).__init__(url_map)

        self.regex = regex


def login_required(view_func):
    """检验用户登录状态装饰器"""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is None:
            resp = {
                "error_code": RET.SESSIONERR,
                "errmsg": "用户未登录"
            }
            return jsonify(resp)
        else:
            g.user_id = user_id
            return view_func(*args, **kwargs)

    return wrapper
