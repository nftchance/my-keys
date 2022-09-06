import requests

from django.conf import settings

TWITCH_CLIENT_ID = settings.TWITCH_CLIENT_ID
TWITCH_SECRET = settings.TWITCH_SECRET


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

        # First get a local access token.
        secretKeyURL = "https://id.twitch.tv/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials".format(
            TWITCH_CLIENT_ID, TWITCH_SECRET)
        r = requests.post(secretKeyURL)
        res = r.json()

        self.access_token = res["access_token"]

    def start():
        print("TwitchManager started")

    def _get_authorized_request(self, url):
        if self.stream_calls[url]:
            return self.stream_calls[url]

        r = requests.get(url, headers={
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": "Bearer " + self.access_token
        })

        self.stream_calls[url] = r

        return r

    def get_user(self, user_id):
        url = f"https://api.twitch.tv/helix/users?id={user_id}"

        if url in self.stream_calls:
            return self.stream_calls[url]

        r = self._get_authorized_request(url)
        res = r.json()

        self.stream_calls[url] = res
        return self.stream_calls[url]

    def get_game(self, game_id):
        url = f"https://api.twitch.tv/helix/games?id={game_id}"

        if url in self.stream_calls:
            return self.stream_calls[url]

        r = self._get_authorized_request(url)
        res = r.json()

        self.stream_calls[url] = res
        return self.stream_calls[url]

    def get_tag(self, tag_id):
        url = f"https://api.twitch.tv/helix/tags/streams?tag_id={tag_id}"

        if url in self.stream_calls:
            return self.stream_calls[url]

        r = self._get_authorized_request(url)
        res = r.json()

        self.stream_calls[url] = res
        return self.stream_calls[url]

    def get_category(self, category_id):
        url = f"https://api.twitch.tv/helix/games?id={category_id}"

        if url in self.stream_calls:
            return self.stream_calls[url]

        r = self._get_authorized_request(url)
        res = r.json()

        self.stream_calls[url] = res
        return self.stream_calls[url]

    def get_streams(self):
        # Get all the streams from the categories and tags.
        for category in self.CATEGORIES:
            self.get_streams_by_category(category)

        for tag in self.TAGS:
            self.get_streams_by_tag(tag)

        return self.stream_calls

    def get_stream(self, stream_id):
        url = f"https://api.twitch.tv/helix/streams?first=100&user_id={stream_id}"

        if url in self.stream_calls:
            return self.stream_calls[url]

        r = self._get_authorized_request(url)
        res = r.json()

        self.stream_calls[url] = res
        return self.stream_calls[url]

    def get_stream_by_user(self, user_id):
        url = f"https://api.twitch.tv/helix/streams?first=100&user_id={user_id}"

        if url in self.stream_calls:
            return self.stream_calls[url]

        r = self._get_authorized_request(url)
        res = r.json()

        self.stream_calls[url] = res
        return self.stream_calls[url]
