from datetime import timedelta
from datetime import datetime
import json

class DouyinNetworkListener:
    def __init__(self):
        self.video_list = []
        self.note = {}

    def handle_response(self, response):
        url = response.url

        # 只抓主页的视频列表接口
        if "aweme/v1/web/aweme/post" in url:
            try:
                data = response.json()
                aweme_list = data.get("aweme_list", [])

                for item in aweme_list:
                    video_info = self.parse_video(item)
                    self.video_list.append(video_info)

            except Exception as e:
                print("解析失败:", e)
        
        # 只抓视频观看页面的AI笔记接口
        if "aweme/v1/web/note/get" in url:
            try:
                data = response.json()
                note_info = data.get("note", {})
                self.note = note_info
            except Exception as e:
                print("解析失败:", e)

    def parse_video(self, item):
        pure_desc, all_text_extra_str = '', ''
        title, desc = '', ''

        # 提取text_extra中的hashtag_name
        first_text_extra = self.get_first_extra(item)

        # desc的三段式：第一行\n第二行\n#标签
        if first_text_extra:
            desc_split = item.get("desc", "").split(f"#{first_text_extra}")
            pure_desc = desc_split[0]
            all_text_extra_str = f"#{first_text_extra}" + desc_split[1] if len(desc_split) > 1 else ""

        desc_split = pure_desc.strip().split("\n")
        title = desc_split[0]
        if len(desc_split) > 1:
            desc = "\n".join(desc_split[1:])
        else:
            desc = all_text_extra_str
        
        # unix时间戳转换为日期字符串，东八区时间
        create_time = item.get("create_time", 0)
        create_time_str = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "aweme_id": item.get("aweme_id"),
            "nickname": item.get("author", {}).get("nickname", ""),
            "title": title,
            "desc": desc,
            "play_url": self.get_play_url(item),
            "create_time": create_time_str,

            "digg_count": item.get("statistics", {}).get("digg_count", 0),
        }

    def get_play_url(self, item):
        try:
            # return item["video"]["play_addr"]["url_list"][0]
            return f"https://www.douyin.com/video/{item.get('aweme_id', "")}"
        except:
            return None
        
    def get_first_extra(self, item):
        text_extra_list = []
        for text_extra in item.get("text_extra", [{}]):
            if text_extra.get("hashtag_name", ""):
                text_extra_list.append(text_extra)
        return text_extra_list[0].get("hashtag_name", "") if len(text_extra_list) > 0 else ""

if __name__ == "__main__":
    listener = DouyinNetworkListener()

    with open("collectors/douyin_crawler/demo_video_list.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data["aweme_list"]:
        video_info = listener.parse_video(item)
        three_days_ago = (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d 00:00:00")
        if video_info["create_time"] > three_days_ago:
            listener.video_list.append(video_info)
    print(listener.video_list)
