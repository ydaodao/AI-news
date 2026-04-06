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
        return {
            "aweme_id": item.get("aweme_id"),
            "desc": item.get("desc"),
            "author": item.get("author", {}).get("nickname"),
            "play_url": self.get_play_url(item),
            # "cover": item.get("video", {}).get("cover", {}).get("url_list", [None])[0],
            "like": item.get("statistics", {}).get("digg_count"),
            "comment": item.get("statistics", {}).get("comment_count"),
        }

    def get_play_url(self, item):
        try:
            # return item["video"]["play_addr"]["url_list"][0]
            return f"https://www.douyin.com/video/{item.get('aweme_id', "")}"
        except:
            return None