# coding: utf-8

import re
from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome import redis_store, db
from ihome.models import User


@api.route("/users", methods=["POST"])
def register():
    """用户注册"""
    # 接收参数，手机号 短信验证码 密码
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")

    # 校验参数
    if not all([mobile, sms_code, password]):
        resp = {
            "error_code": RET.PARAMERR,
            "errmsg": "参数不完整"
        }
        return jsonify(resp)

    if not re.match(r"1[34578]\d{9}", mobile):
        resp = {
            "error_code": RET.DATAERR,
            "errmsg": "手机号格式错误"
        }
        return jsonify(resp)

    # 业务处理
    # 获取真实的短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        resp = {
            "error_code": RET.DBERR,
            "errmsg": "查询短信验证码错误"
        }
        return jsonify(resp)

    # 判断短信验证码是否过期
    if real_sms_code is None:
        resp = {
            "error_code": RET.NODATA,
            "errmsg": "短信验证码已过期"
        }
        return jsonify(resp)

    # 判断用户输入的短信验证码是否正确
    if real_sms_code != sms_code:
        resp = {
            "error_code": RET.DATAERR,
            "errmsg": "短信验证码错误"
        }
        return jsonify(resp)

    # 删除短信验证码
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 判断手机号是否已经注册
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     resp = {
    #         "error_code": RET.DBERR,
    #         "errmsg": "数据库异常"
    #     }
    #     return jsonify(resp)
    #
    # if user is not None:
    #     resp = {
    #         "error_code": RET.DATAEXIST,
    #         "errmsg": "手机号已经注册"
    #     }
    #     return jsonify(resp)

    # 保存用户的数据到数据库中
    user = User(name=mobile, mobile=mobile)
    # 对于password属性的设置，会调用属性方法
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        resp = {
                "error_code": RET.DATAEXIST,
                "errmsg": "手机号已经注册"
            }
        return jsonify(resp)

    # 记录用户的登录状态
    session["user_id"] = user.id
    session["username"] = mobile
    session["mobile"] = mobile

    # 返回响应
    resp = {
        "error_code": RET.OK,
        "errmsg": "注册成功"
    }
    return jsonify(resp)


@api.route("/session", methods=["POST"])
def login():
    """登录"""
    # 获取参数, 用户名  密码
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")

    # 校验参数
    if not all([mobile, password]):
        resp = {
            "error_code": RET.PARAMERR,
            "errmsg": "参数不完整"
        }
        return jsonify(resp)

    # 业务处理
    try:
        user = User.query.filter_by(name=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            if user.check_password(password):
                # 记录用户的登录状态
                session["user_id"] = user.id
                session["username"] = mobile
                session["mobile"] = mobile

                resp = {
                    "error_code": RET.OK,
                    "errmsg": "登录成功"
                }
                return jsonify(resp)
            else:
                resp = {
                    "error_code": RET.DATAERR,
                    "errmsg": "密码错误"
                }
                return jsonify(resp)
        else:
            resp = {
                "error_code": RET.NODATA,
                "errmsg": "用户名不存在"
            }
            return jsonify(resp)


@api.route("/session", methods=["GET"])
def check_login():
    """检查用户的登录状态"""
    username = session.get("username")
    if username is not None:
        resp = {
            "error_code": RET.OK,
            "errmsg": "true",
            "username": username
        }
        return jsonify(resp)
    else:
        resp = {
            "error_code": RET.SESSIONERR,
            "errmsg": "false"
        }
        return jsonify(resp)


@api.route("/session", methods=["DELETE"])
def logout():
    """退出"""
    session.clear()
    resp = {
        "error_code": RET.OK,
        "errmsg": "退出成功"
    }
    return jsonify(resp)
