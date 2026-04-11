import os, sys
print("当前工作目录是:", sys.path) 

from feishu.robot_service import BotService, build_event_handler, load_bot_templates
from feishu.robot_utils import build_client, build_ws_client, load_settings

def main():
    print("Starting bot...")

    settings = load_settings()
    client = build_client(settings)
    bot = BotService(client=client)
    event_handler = build_event_handler(bot)
    ws_client = build_ws_client(settings, event_handler=event_handler)

    ws_client.start()


if __name__ == "__main__":
    main()
