# coding:utf-8

from . import api
from flask import g, current_app, jsonify, request
from ihome.utils.response_code import RET
from ihome.utils.commons import login_required
from datetime import datetime
from ihome.models import House, Order
from ihome import db, redis_store


@api.route("/orders", methods=["POST"])
@login_required
def save_order():
    """保存订单"""
    # 获取用户id
    user_id = g.user_id

    # 获取参数
    order_data = request.get_json()
    if not order_data:
        return jsonify(error_code=RET.PARAMERR, errmsg="参数错误")

    house_id = order_data.get("house_id")  # 预定的房屋编号
    start_data_str = order_data.get("start_date")  # 预定的起始时间
    end_data_str = order_data.get("end_date")  # 预定的结束时间

    # 参数校验
    if not all([house_id, start_data_str, end_data_str]):
        return jsonify(error_code=RET.PARAMERR, errmsg="参数不完整")

    # 日期格式检验
    try:
        # 将请求的时间参数字符串转换为datetime类型
        start_date = datetime.strptime(start_data_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_data_str, "%Y-%m-%d")
        assert start_date <= end_date
        # 计算预定的天数
        days = (end_date - start_date).days + 1
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.PARAMERR, errmsg="日期格式错误")

    # 查询房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.DBERR, errmsg="获取房屋信息失败")
    if not house:
        return jsonify(error_code=RET.NODATA, errmsg="房屋不存在")

    # 预定的房屋是否是房东自己的
    if user_id == house.user_id:
        return jsonify(error_code=RET.ROLEERR, errmsg="不能预定自己的房屋")

    # 确保用户预定的时间内，房屋没有被别人下单
    try:
        # 查询时间冲突的订单
        count = Order.query.filter(Order.house_id == house.id, Order.begin_date <= end_date,
                                   Order.end_date >= start_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.DBERR, errmsg="检查出错，请稍后再试")
    if count > 0:
        return jsonify(error_code=RET.DATAERR, errmsg="房屋已被预定")

    # 订单总额
    amount = days * house.price

    # 保存订单数据
    order = Order()
    order.house_id = house_id
    order.user_id = user_id
    order.begin_date = start_date
    order.end_date = end_date
    order.days = days
    order.house_price = house.price
    order.amount = amount
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error_code=RET.DBERR, errmsg="保存订单失败")
    return jsonify(error_code=RET.OK, errmsg="ok", data={"order_id": order.id})


@api.route("/user/orders", methods=["GET"])
@login_required
def get_user_orders():
    """查询用户的订单信息"""
    user_id = g.user_id

    # 用户的身份，用户想要查询作为房客预定别人房子的订单，还是想要作为房东查询别人预定自己房子的订单
    role = request.args.get("role", "")

    # 查询订单数据
    try:
        if "landlord" == role:
            print "--------------1--------------------"
            # 以房东的身份查询订单
            # 先查询属于自己的房子有哪些
            houses = House.query.filter(House.user_id == user_id).all()
            houses_ids = [house.id for house in houses]
            # 再查询预定了自己房子的订单
            orders = Order.query.filter(Order.house_id.in_(houses_ids)).order_by(Order.create_time.desc())
        else:
            # 以房客的身份查询订单，查询自己预定的订单
            orders = Order.query.filter(Order.user_id == user_id).order_by(Order.create_time.desc())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.DBERR, errmsg="查询订单信息失败")

    # 将订单对象转换为字典数据
    orders_dict_list = []
    if orders:
        for order in orders:
            orders_dict_list.append(order.to_dict())

    return jsonify(error_code=RET.OK, errmsg="ok", data={"orders": orders_dict_list})


@api.route("/orders/<int:order_id>/status", methods=["PUT"])
@login_required
def accept_reject_order(order_id):
    """接单、拒单"""
    user_id = g.user_id

    # 获取参数
    req_data = request.get_json()
    if not req_data:
        return jsonify(error_code=RET.PARAMERR, errmsg="参数错误")

    # action参数表明客户端请求的是接单还是拒单的行为
    action = req_data.get("action")
    if action not in ("accept", "reject"):
        return jsonify(error_code=RET.PARAMERR, errmsg="参数错误")

    try:
        # 根据订单号查询订单，并且要求订单处于等待接单状态
        order = Order.query.filter(Order.id == order_id, Order.status == "WAIT_ACCEPT").first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.DBERR, errmsg="无法获取订单数据")

    # 确保房东只能修改属于自己房子的订单
    if not order or house.user_id != user_id:
        return jsonify(error_code=RET.REQERR, errmsg="操作无效")

    if action == "accept":
        # 接单，将订单状态设置为等待评论
        order.status = "WAIT_PAYMENT"
    elif action == "reject":
        # 拒单，要求用户传递拒单原因
        reason = req_data.get("reason")
        if not reason:
            return jsonify(error_code=RET.PARAMERR, errmsg="参数错误")
        order.status = "REJECTED"
        order.comment = reason

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error_code=RET.DBERR, errmsg="操作失败")

    return jsonify(error_code=RET.OK, errmsg="OK")


@api.route("/orders/<int:order_id>/comment", methods=["PUT"])
@login_required
def save_order_comment(order_id):
    """保存订单评论信息"""
    user_id = g.user_id
    # 获取参数
    req_data = request.get_json()
    comment = req_data.get("comment")  # 评价信息

    # 检查参数
    if not comment:
        return jsonify(error_code=RET.PARAMERR, errmsg="参数错误")

    try:
        # 需要确保只能评论自己下的订单，而且订单处于待评价状态才可以
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id,
                                   Order.status == "WAIT_COMMENT").first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.DBERR, errmsg="无法获取订单数据")

    if not order:
        return jsonify(error_code=RET.REQERR, errmsg="操作无效")

    try:
        # 将订单的状态设置为已完成
        order.status = "COMPLETE"
        # 保存订单的评价信息
        order.comment = comment
        # 将房屋的完成订单数增加1
        house.order_count += 1
        db.session.add(order)
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error_code=RET.DBERR, errmsg="操作失败")

    # 因为房屋详情中有订单的评价信息，为了让最新的评价信息展示在房屋详情中，所以删除redis中关于本订单房屋的详情缓存
    try:
        redis_store.delete("house_info_%s" % order.house.id)
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(error_code=RET.OK, errmsg="OK")



















