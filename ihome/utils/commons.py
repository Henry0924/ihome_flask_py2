# coding:utf-8

from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    """自定义的接收正则表达式的转换器"""
    def __init__(self, url_map, regex):
        """regex是在路由中填写的正则表达式"""
        super(RegexConverter, self).__init__(url_map)

        self.regex = regex
