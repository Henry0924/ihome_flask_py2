# coding:utf-8

from . import api
from flask import g, request, jsonify, current_app, session
from ihome.utils.commons import login_required
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage
from ihome.models import User
from ihome import constants, db


@api.route("/users/avatar", methods=["POST"])
@login_required
def set_user_avatar():
    """设置用户头像"""
    # 获取参数， 头像图片   用户
    user_id = g.user_id
    image_file = request.files.get("avatar")

    # 校验参数
    if image_file is None:
        # 表示用户没有上传头像
        return jsonify(error_code=RET.PARAMERR, errmsg="未上传头像")

    # 保存用户头像数据
    image_data = image_file.read()
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.THIRDERR, errmsg="上传头像异常")

    # 将文件名保存到数据库中
    try:
        User.query.filter_by(id=user_id).update({"avatar_url": file_name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error_code=RET.DBERR, errmsg="保存头像信息失败")

    avatar_url = constants.QINIU_URL_DOMAIN + file_name
    # 返回值
    return jsonify(error_code=RET.OK, errmsg="保存头像成功", data={"avatar_url": avatar_url})


@api.route("/users/real_name", methods=["POST"])
@login_required
def save_real_name():
    """实名认证"""
    # 获取用户id
    user_id = g.user_id
    # 获取参数
    req_dict = request.get_json()
    if not req_dict:
        return jsonify(error_code=RET.PARAMERR, errmsg="参数不完整")
    real_name = req_dict.get("real_name")
    id_card = req_dict.get("id_card")

    # 校验参数
    if not all([real_name, id_card]):
        return jsonify(error_code=RET.PARAMERR, errmsg="实名信息不完整")

    # 业务处理
    # 保存实名信息
    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None)\
            .update({"real_name": real_name, "id_card": id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error_code=RET.DBERR, errmsg="保存实名信息失败")

    return jsonify(error_code=RET.OK, errmsg="实名成功")


@api.route("/users/real_name", methods=["GET"])
@login_required
def get_real_name():
    """获取实名信息"""
    # 获取用户id
    user_id = g.user_id

    # 获取用户实名信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.DBERR, errmsg="查询实名信息失败")

    if user is None:
        return jsonify(error_code=RET.NODATA, errmsg="未实名")

    # 返回值
    return jsonify(error_code=RET.OK, errmsg="ok", data=user.auth_to_dict())


@api.route("/users/name", methods=["PUT"])
@login_required
def set_user_name():
    """设置用户名"""
    # 获取用户id
    user_id = g.user_id
    # 获取参数
    req_dict = request.get_json()
    username = req_dict.get("username")

    # 校验参数
    if username is None:
        return jsonify(error_code=RET.PARAMERR, errmsg="新用户名不能为空")

    # 业务处理
    try:
        User.query.filter_by(id=user_id).update({"name": username})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error_code=RET.DBERR, errmsg="设置用户名失败")

    # 返回值, 修改session中的name字段
    session["username"] = username
    return jsonify(error_code=RET.OK, errmsg="设置成功", data={"username": username})


@api.route("/users/info", methods=["GET"])
@login_required
def get_user_info():
    """获取用户信息"""
    # 获取用户id
    user_id = g.user_id

    # 获取用户信息
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.DBERR, errmsg="用户信息查询失败")

    if user is not None:
        avatar_url = constants.QINIU_URL_DOMAIN + user.avatar_url
        username = user.name
        mobile = user.mobile
        return jsonify(error_code=RET.OK, errmsg="获取用户信息成功",
                       data={"avatar_url": avatar_url,
                             "username": username,
                             "user_mobile": mobile})
