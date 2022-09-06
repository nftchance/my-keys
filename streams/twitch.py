import requests

from django.conf import settings

TWITCH_CLIENT_ID = settings.TWITCH_CLIENT_ID

class TwitchManager:
    # Find all the developer streams on Twitch

    CATEGORIES = [
        "Just Chatting",
        "Science & Technology",
        "Software Development",
    ]

    TAGS = [ 
        "programming",
        "coding",
    ]

    def __init__(self):
        self.stream_calls = {}
        self.streams = {}

    def start():
        print("TwitchManager started")

    def _get_authorized_request(self, url):
        return requests.get(url, headers={"Client-ID": TWITCH_CLIENT_ID})

    def get_streams_by_category(self, category):
        url = f"https://api.twitch.tv/helix/streams?first=100&game_id={category}"

        if url in self.stream_calls:
            return self.stream_calls[url]

        r = self._get_authorized_request(url)
        res = r.json()

        self.stream_calls[url] = res

        return self.stream_calls[url]
    
    def get_streams_by_tag(self, tag):
        url = f"https://api.twitch.tv/helix/streams?first=100&tag_id={tag}"

        if url in self.stream_calls:
            return self.stream_calls[url]

        r = self._get_authorized_request(url)
        res = r.json()

        self.stream_calls[url] = res

        return self.stream_calls[url]