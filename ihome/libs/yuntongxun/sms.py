# coding=utf-8


from CCPRestSDK import REST
import ConfigParser

# 主帐号
accountSid = '8aaf070863399ed901634cc815e20e62'

# 主帐号Token
accountToken = '04242a9c509347c3b3334eab1ac9a2f1'

# 应用Id
appId = '8aaf070863399ed901634cc8163b0e69'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'


# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id


class CCP(object):
    """发送短信的工具类 单例模式"""
    instance = None

    def __new__(cls, *args, **kwargs):
        # 判断CCP中有没有类属性instance
        if cls.instance is None:
            cls.instance = super(CCP, cls).__new__(cls)

            # 初始化REST SDK
            cls.instance.rest = REST(serverIP, serverPort, softVersion)
            cls.instance.rest.setAccount(accountSid, accountToken)
            cls.instance.rest.setAppId(appId)

        return cls.instance

    def send_template_sms(self, to, datas, temp_id):
        try:
            # 调用云通讯的工具rest发送短信
            result = self.rest.sendTemplateSMS(to, datas, temp_id)
        except Exception as e:
            raise e
        # result 返回值
        # {'templateSMS': {'smsMessageSid': '4a4f0e64fce147ac8998ac8404e9b060',
        # 'dateCreated': '20180512195528'}, 'statusCode': '000000'}
        status_code = result.get("statusCode")
        if status_code == '000000':
            # 表示发送成功
            return 0
        else:
            # 表示发送失败
            return -1


if __name__ == '__main__':
    ccp = CCP()
    ccp.send_template_sms("13477096357", ["123456", 5], 1)
