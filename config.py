# coding:utf-8

import redis


class Config(object):
    """工程的配置信息"""

    SECRET_KEY = "osieje384jfn*kok"

    # 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome_py2"

    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask_session用到的配置信息
    SESSION_TYPE = "redis"  # 指明将session保存到redis数据库中
    SESSION_USE_SIGNER = True  # 让cookie中的session_id被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 生成redis实例
    PERMANENT_SESSION_LIFETIME = 86400  # 设置session的有效时间


class DevConfig(Config):
    """开发模式使用的配置信息"""
    DEBUG = True

    # 支付宝
    ALIPAY_APPID = "2016091400512796"
    ALIPAY_URL = "https://openapi.alipaydev.com/gateway.do"


class ProConfig(Config):
    """生产模式 线上模式的配置信息"""
    pass


config_dict = {
    "develop": DevConfig,
    "product": ProConfig
}