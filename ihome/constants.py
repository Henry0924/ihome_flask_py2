# coding:utf-8

# 常量
IMAGE_CODE_REDIS_EXPIRES = 120  # 图片验证码redis保存的有效期，秒

SMS_CODE_REDIS_EXPIRES = 300  # 图片验证码redis保存的有效期，秒

QINIU_URL_DOMAIN = "http://p8ra3ebbx.bkt.clouddn.com/"

LOGIN_ERROR_MAX_NUM = 5   # 登录的最大错误次数

LOGIN_ERROR_FORBID_TIME = 10  # 登录错误封ip的时间，秒

AREA_INFO_REDIS_EXPIRES = 3600  # 地区信息在redis中的有效期，秒

HOME_PAGE_MAX_HOUSES = 5  # 首页轮播图最大数量

HOME_PAGE_DATA_REDIS_EXPIRES = 3600  # 首页房屋轮播图中redis中有效期

HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 10  # 房屋详情页评论的显示数量

HOUSE_DETAIL_REDIS_EXPIRE_SECOND = 7200  # 房屋详情信息在redis中有效期

HOUSE_LIST_PAGE_CAPACITY = 2  # 房屋列表页每页显示个数

HOUSE_LIST_PAGE_REDIS_EXPIRES = 3600  # 房屋列表数据在redis中的有效期






