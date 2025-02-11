from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
import os


def create_client(access_key_id, access_key_secret):
    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret
    )
    config.endpoint = f'dysmsapi.aliyuncs.com'
    return Dysmsapi20170525Client(config)

def send_sms(phone, code):
    access_key_id = os.environ.get('ALIYUN_ACCESS_KEY_ID')                          # 阿里云 access_key_id, 未来要修改
    access_key_secret = os.environ.get('ALIYUN_ACCESS_KEY_SECRET')                  # 阿里云 access_key_secret  未来要修改
    sign_name = os.environ.get('ALIYUN_SMS_SIGN_NAME')                              # 阿里云短信签名  未来要修改
    template_code = 'SMS_478595613'                                             # 阿里云短信模板     未来要修改

    client = create_client(access_key_id, access_key_secret)
    send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
        sign_name= sign_name,
        template_code=template_code,
        phone_numbers=phone,
        template_param='{"code":"' + code + '"}'
    )

    runtime = util_models.RuntimeOptions()
    try:
        # 复制代码运行请自行打印 API 的返回值
        response = client.send_sms_with_options(send_sms_request, runtime)
        print('短信发送成功, 结果是:',response.body)
    except Exception as error:
        # 如有需要，请打印 error
        UtilClient.assert_as_string(error.message)
        print("短信发送失败", error.message)
    return send_sms_request

