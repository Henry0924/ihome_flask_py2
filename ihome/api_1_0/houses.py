# coding:utf-8

import json
from . import api
from ihome import redis_store, constants, db
from ihome.models import Area, House, HouseImage, Facility, User, Order
from flask import current_app, jsonify, g, request, session
from ihome.utils.response_code import RET
from ihome.utils.commons import login_required
from ihome.utils.image_storage import storage
from datetime import datetime


@api.route("/areas")
def get_area_info():
    """获取城区信息"""
    # 先从redis中尝试获取城区信息
    try:
        areas_json = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
        areas_json = None

    if areas_json is None:
        # 查询数据库获取城区信息
        try:
            areas_list = Area.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(error_code=RET.DBERR, errmsg="查询城区信息异常")

        # 遍历列表，处理每一个对象，转换一下对象的属性名
        areas = []
        for area in areas_list:
            areas.append(area.to_dict())

        # 将数据转换为json
        areas_json = json.dumps(areas)
        # 将数据在redis中保存一份缓存
        try:
            redis_store.setex("area_info", constants.AREA_INFO_REDIS_EXPIRES, areas_json)
        except Exception as e:
            current_app.logger.error(e)

    return '{"error_code": 0, "errmsg": "查询城区信息成功", "data": {"areas": %s}}' % areas_json, 200, \
           {"Content-Type": "application/json"}


@api.route("/houses/info", methods=["POST"])
@login_required
def set_house_info():
    """设置房屋信息
    前端发送来的json数据
    {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["7","8"]
    }
    """
    # 获取参数
    house_data = request.get_json()
    if not house_data:
        return jsonify(error_code=RET.PARAMERR, errmsg="参数不完整")

    title = house_data.get("title")
    price = house_data.get("price")
    area_id = house_data.get("area_id")
    address = house_data.get("address")
    room_count = house_data.get("room_count")
    acreage = house_data.get("acreage")
    unit = house_data.get("unit")
    capacity = house_data.get("capacity")
    beds = house_data.get("beds")
    deposit = house_data.get("deposit")
    min_days = house_data.get("min_days")
    max_days = house_data.get("max_days")

    # 参数校验
    if not all([title, price, area_id, address, room_count, acreage,
                unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(error_code=RET.PARAMERR, err_msg="参数不完整")

    # 判断price 和 deposit
    try:
        price = int(float(price) * 100)
        deposit = int(float(price) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.PARAMERR, errmsg="参数有误")

    # 业务处理
    # 保存房屋信息
    user_id = g.user_id

    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # 获取房屋的设施信息
    facility_id_list = house_data.get("facility")
    if facility_id_list:
        # 用户勾选了设施
        # 筛选掉不合理的设施
        try:
            facility_list = Facility.query.filter(Facility.id.in_(facility_id_list)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(error_code=RET.DBERR, errmsg="数据库异常")

        if facility_list:
            house.facilities = facility_list

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error_code=RET.DBERR, errmsg="保存房屋信息失败")

    # 返回值
    return jsonify(error_code=RET.OK, errmsg="保存成功", data={"house_id": house.id})


@api.route("/houses/image", methods=["POST"])
@login_required
def set_house_image():
    """设置房屋图片"""
    # 获取房屋id  房屋图片
    house_id = request.form.get("house_id")
    house_image = request.files.get("house_image")

    # 校验参数
    if not all([house_id, house_image]):
        return jsonify(error_code=RET.PARAMERR, err_msg="参数不完整")

    # 判断房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.DBERR, errmsg="数据库异常")

    if house is None:
        return jsonify(error_code=RET.NODATA, errmsg="房屋不存在")

    # 上传图片到七牛云
    image_data = house_image.read()
    try:
        image_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.THIRDERR, errmsg="上传异常")

    # 将图片名保存到数据库
    h_image = HouseImage(
        house_id=house_id,
        url=image_name
    )
    db.session.add(h_image)

    if not house.index_image_url:
        house.index_image_url = image_name
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error_code=RET.DBERR, errmsg="保存图片信息失败")

    image_url = constants.QINIU_URL_DOMAIN + image_name
    return jsonify(error_code=RET.OK, errmsg="保存图片成功", data={"image_url": image_url})


@api.route("/user/houses", methods=["GET"])
@login_required
def get_user_houses():
    """获取房东发布的房源信息"""
    # 获取用户id
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.DBERR, errmsg="获取数据失败")

    # 将查询到的房屋信息转换为字典存放到列表中
    houses_list = []
    if houses:
        for house in houses:
            houses_list.append(house.to_basic_dict())

    return jsonify(error_code=RET.OK, errmsg="ok", data={"houses": houses_list})


@api.route("/houses/index", methods=["GET"])
def get_house_index():
    """获取主页幻灯片展示的房屋基本信息"""
    # 尝试从缓存中获取
    try:
        ret = redis_store.get("home_page_data")
    except Exception as e:
        current_app.logger.error(e)
        ret = None

    if ret:
        current_app.logger.info("hit house index info redis")
        # 因为redis中保存的是json字符串，所以值直接进行字符串拼接返回
        return '{"error_code": 0, "errmsg": "ok", "data": %s}' % ret, 200, {"Content-Type": "application/json"}
    else:
        try:
            # 查询数据库，返回房屋订单数目最多的5条数据
            houses = House.query.order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(error_code=RET.DBERR, errmsg="查询数据失败")

        if not houses:
            return jsonify(error_code=RET.NODATA, errmsg="查询无数据")

        houses_list = []
        for house in houses:
            # 如果房屋未设置主图片，则跳过
            if not house.index_image_url:
                continue
            houses_list.append(house.to_basic_dict())

        # 将数据转换为json，并保存到redis缓存
        json_houses = json.dumps(houses_list)
        try:
            redis_store.setex("home_page_data", constants.HOME_PAGE_DATA_REDIS_EXPIRES, json_houses)
        except Exception as e:
            current_app.logger.error(e)

        return '{"error_code": 0, "errmsg": "ok", "data": %s}' % json_houses, 200, {"Content-Type": "application/json"}


@api.route("/houses/<int:house_id>", methods=["GET"])
def get_house_detail(house_id):
    """获取房屋详情"""
    # 前端在房屋详情页面展示时，如果浏览页面的用户不是该屋的房东，则展示预定按钮，否则不展示
    # 所以需要后端返回登录用户的id
    # 尝试获取用户登录的信息，若登录，则返回给前端登录用户的id，否则返回user_id = -1
    user_id = session.get("user_id", "-1")

    # 校验参数
    if not house_id:
        return jsonify(error_code=RET.PARAMERR, errmsg="缺少参数")

    # 先从redis缓存中获取信息
    try:
        ret = redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    if ret:
        current_app.logger.info("hit house info redis")
        return '{"error_code": 0, "errmsg":"ok", "data":{"user_id":%s, "house":%s}}' % (user_id, ret), \
               200, {"Content-Type": "application/json"}

    # 查询数据库
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.DBERR, errmsg="查询数据失败")

    if not house:
        return jsonify(error_code=RET.NODATA, errmsg="房屋不存在")

    # 将房屋对象数据转换为字典
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.DATAERR, errmsg="数据出错")

    # 存入到redis中
    json_house = json.dumps(house_data)
    try:
        redis_store.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, json_house)
    except Exception as e:
        current_app.logger.error(e)

    resp = '{"error_code":0, "errmsg":"ok", "data":{"user_id": %s, "house": %s}}' % (user_id, json_house), \
           200, {"Content-Type": "application/json"}

    return resp


@api.route("/houses", methods=["GET"])
def get_house_list():
    """获取房屋列表信息"""
    # 获取参数
    start_date_str = request.args.get("sd", "")  # 想要查询的起始时间
    end_date_str = request.args.get("ed", "")  # 想要查询的终止时间
    area_id = request.args.get("aid", "")  # 区域id
    sort_key = request.args.get("sk", "new")  # 排序关键字
    page = request.args.get("p", 1)  # 页数

    # 校验参数
    # 判断日期
    try:
        start_date = None
        if start_date_str:
            start_date = datetime.strftime(start_date_str, "%Y-%m-%d")

        end_date = None
        if end_date_str:
            end_date = datetime.strftime(end_date_str, "%Y-%m-%d")

        if start_date and end_date:
            assert start_date <= end_date

    except Exception as e:
        return jsonify(error_code=RET.PARAMERR, errmsg="日期参数有误")

    # 判断页数
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # 先从redis缓存中获取数据
    try:
        redis_key = "houses_%s_%s_%s_%s" % (start_date_str, end_date_str, area_id, sort_key)
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
        resp_json = None
    if resp_json:
        # 从redis缓存中获取到了数据
        return resp_json, 200, {"Content-Type": "application/json"}

    # 查询数据
    filter_params = []

    # 处理区域信息
    if area_id:
        filter_params.append(House.area_id == area_id)

    # 处理时间
    try:
        conflict_orders_li = []
        if start_date and end_date:
            # 从订单表中查询冲突的订单，进而获取冲突的房屋id
            conflict_orders_li = Order.query.filter(Order.begin_date <= end_date, Order.end_date >= start_date).all()

        elif start_date:
            # 从订单表中查询冲突的订单，进而获取冲突的房屋id
            conflict_orders_li = Order.query.filter(Order.end_date >= start_date).all()

        elif end_date:
            # 从订单表中查询冲突的订单，进而获取冲突的房屋id
            conflict_orders_li = Order.query.filter(Order.begin_date <= end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.DBERR, errmsg="数据库异常")

    if conflict_orders_li:
        conflict_orders_id_li = [order.house_id for order in conflict_orders_li]
        # 添加条件，查询不冲突的房屋
        filter_params.append(House.id.notin_(conflict_orders_id_li))

    # 排序
    if sort_key == "booking":
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == "price-inc":
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == "price-des":
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    # 分页
    try:
        house_page = house_query.paginate(page, constants.HOUSE_LIST_PAGE_CAPACITY, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_code=RET.DBERR, errmsg="数据库异常")

    house_li = house_page.items  # 当前页中的数据结果
    total_page = house_page.pages  # 总页数

    houses = []
    for house in house_li:
        houses.append(house.to_basic_dict())

    # 将结果缓存到redis中
    # 将结果转换成json字符串
    resp = dict(error_code=RET.OK, errmsg="查询成功",
                data={"houses": houses, "total_page": total_page, "current_page": page})
    resp_json = json.dumps(resp)

    if page <= total_page:
        # 用redis的哈希类型保存分页数据
        redis_key = "houses_%s_%s_%s_%s" % (start_date_str, end_date_str, area_id, sort_key)
        try:
            # 使用redis中的事务
            pipeline = redis_store.pipeline()
            # 开启事务
            pipeline.multi()
            pipeline.hset(redis_key, page, resp_json)
            pipeline.expire(redis_key, constants.HOUSE_LIST_PAGE_REDIS_EXPIRES)
            # 执行事务
            pipeline.execute()
        except Exception as e:
            current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}
