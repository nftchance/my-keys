import requests

from django.conf import settings

from .models import Stream

TWITCH_CLIENT_ID = settings.TWITCH_CLIENT_ID
TWITCH_SECRET = settings.TWITCH_SECRET


class TwitchManager:
    # Find all the developer streams on Twitch
    CATEGORIES = [
        "Science & Technology",
        "Software Development",
    ]

    TAGS = [
        "web3",
        "solidity",
        "hardhat",
        "truffle",
        "ethereum",
        "foundry",
        "decentralized",
        "nft",
        "crypto",
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

    def start_listening(self):
        print("TwitchManager started listening")

        for category in self.CATEGORIES:
            for stream in self.get_category(category):
                self._retrieve_or_create_stream(stream)

    def start_watching(self):
        print("TwitchManager started watching")

    def sync_stream(self, stream):
        # Get all the streams from Twitch
        # TODO: Save this object into the database
        pass

    def sync_streams(self, streams):
        for stream in streams:
            self.sync_stream(stream)

    def _retrieve_or_create_stream(self, stream):
        stream, created = Stream.objects.get_or_create(
            stream_id=stream["id"])

        if created:
            print('Created stream', stream.full_name)

        return stream

    def _get_authorized_request(self, url):
        if url in self.stream_calls:
            return self.stream_calls[url]

        r = requests.get(url, headers={
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": "Bearer " + self.access_token
        })

        self.stream_calls[url] = r

        return r.json()

    def get_user(self, user_id):
        url = f"https://api.twitch.tv/helix/users?id={user_id}"

        return self._get_authorized_request(url)

    def get_game(self, game_id):
        url = f"https://api.twitch.tv/helix/games?id={game_id}"

        return self._get_authorized_request(url)

    def get_tag(self, tag_id):
        url = f"https://api.twitch.tv/helix/tags/streams?tag_id={tag_id}"

        return self._get_authorized_request(url)

    def get_category(self, category_id):
        url = f"https://api.twitch.tv/helix/games?id={category_id}"

        return self._get_authorized_request(url)

    def get_streams(self):
        streams = []

        # Get all the streams from the categories and tags.
        for category in self.CATEGORIES:
            streams.append(self.get_category(category))

        for tag in self.TAGS:
            streams.append(self.get_tag(tag))

        # flatten streams array
        return [item for sublist in streams for item in sublist]

    def get_live_streams(self, streams=None):
        if streams is None:
            streams = self.get_streams()

        live_streams = []

        for stream in streams["data"]:
            if stream["type"] == "live":
                live_streams.append(stream)

        return live_streams

    def get_filtered_streams(self, streams=None, tags=TAGS, max_viewers=-1):
        if streams is None:
            streams = self.get_live_streams()

        filtered_streams = []

        for stream in streams:
            viewer_conforming = stream["viewer_count"] <= max_viewers or max_viewers == -1
            tag_collision = any(
                tag in stream["tag_ids"] or tag in stream["title"] for tag in tags)

            if viewer_conforming and tag_collision:
                filtered_streams.append(stream)

        return filtered_streams

    def get_vods(self, user_id):
        url = f"https://api.twitch.tv/helix/videos?user_id={user_id}"

        return self._get_authorized_request(url)
