# coding:utf-8

from flask import Blueprint, current_app, make_response
from flask_wtf.csrf import generate_csrf


html = Blueprint("html", __name__)


# 提供静态的html文件
@html.route("/<re(r'.*'):file_name>")
def get_html_file(file_name):
    """提供html静态文件"""
    # 根据用户访问的路径提供相应的html文件
    if not file_name:
        # 如果用户访问的是/
        file_name = "index.html"

    if file_name != "favicon.ico":
        file_name = "html/" + file_name

    # 生产csrf_token字符串
    csrf_token = generate_csrf()

    # 为用户设置cookie，csrf_token
    resp = make_response(current_app.send_static_file(file_name))
    resp.set_cookie("csrf_token", csrf_token)

    return resp
