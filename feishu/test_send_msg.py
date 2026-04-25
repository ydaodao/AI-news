import json

import lark_oapi as lark
from lark_oapi.api.im.v1 import *

from feishu.robot_service import MsgBotService


# SDK 使用说明: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development
# 以下示例代码默认根据文档示例值填充，如果存在代码问题，请在 API 调试台填上相关必要参数后再复制代码使用
# 复制该 Demo 后, 需要将 "YOUR_APP_ID", "YOUR_APP_SECRET" 替换为自己应用的 APP_ID, APP_SECRET.
def main():
    # bot = BotService(client=build_client(load_settings()))

    # 构造请求对象
    template_variable = {
        "news_list": [
            {
                "title": "测试标题",
                "content": "测试内容",
                "url": "https://www.baidu.com",
            }
        ]
    }
    # response: CreateMessageResponse = bot.send_ai_news_card(template_variable=template_variable)

    MsgBotService().send_ai_news_card(template_variable=template_variable)

    # 发起请求
    # client.im.v1.message.create(request)

    # 处理失败返回
    # if not response.success():
    #     lark.logger.error(
    #         f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
    #     return

    # # 处理业务结果
    # lark.logger.info(f"client.im.v1.message.create success, msg_id: {response}")
    # lark.logger.debug(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    main()
