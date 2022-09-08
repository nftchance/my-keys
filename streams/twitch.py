import re
import httpx
import os
import requests

from django.conf import settings

from .models import Stream

TWITCH_CLIENT_ID = settings.TWITCH_CLIENT_ID
TWITCH_SECRET = settings.TWITCH_SECRET

GQL_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"


class HTTPError(Exception):
    def __init__(self, errors):
        super().__init__("HTTP request failed")
        self.errors = errors


class GQLError(Exception):
    def __init__(self, errors):
        super().__init__("GraphQL query failed")
        self.errors = errors


class TwitchManager:
    # Find all the developer streams on Twitch
    CATEGORIES = [
        "509670",  # Science & Technology
        "1469308723",  # Software Development
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
        "blockchain",
        "smart contract",
    ]

    VIDEO_FIELDS = """
        id
        title
        publishedAt
        broadcastType
        lengthSeconds
        game {
            name
        }
        creator {
            login
            displayName
        }
    """

    CLIP_FIELDS = """
        id
        slug
        title
        createdAt
        viewCount
        durationSeconds
        url
        videoQualities {
            frameRate
            quality
            sourceURL
        }
        game {
            id
            name
        }
        broadcaster {
            displayName
            login
        }
    """

    def __init__(self):
        self.stream_calls = {}
        self.streams = {}

        # First get a local access token.
        url = f"https://id.twitch.tv/oauth2/token?client_id={TWITCH_CLIENT_ID}&client_secret={TWITCH_SECRET}&grant_type=client_credentials"
        r = requests.post(url)
        res = r.json()

        self.access_token = res["access_token"]

    def start_listening(self):
        print("TwitchManager started listening")

        for stream in self.get_filtered_streams():
            self._retrieve_or_create_stream(stream)

    # use twitch-dl to download videos from twitch
    def start_downloads(self):
        print("TwitchManager started watching")

        for stream in Stream.objects.filter(downloaded=False):
            self._get_media(stream)

    def get_gql_access_token(self, video_id, auth_token=None):
        query = """
        {{
            videoPlaybackAccessToken(
                id: {video_id},
                params: {{
                    platform: "web",
                    playerBackend: "mediaplayer",
                    playerType: "site"
                }}
            ) {{
                signature
                value
            }}
        }}
        """

        query = query.format(video_id=video_id)

        headers = {}
        if auth_token is not None:
            headers['authorization'] = f'OAuth {auth_token}'

        try:
            response = self.gql_query(query, headers=headers)
            return response["data"]["videoPlaybackAccessToken"]
        except httpx.HTTPStatusError as error:
            # Provide a more useful error message when server returns HTTP 401
            # Unauthorized while using a user-provided auth token.
            if error.response.status_code == 401:
                if auth_token:
                    raise HTTPError(
                        "Unauthorized. The provided auth token is not valid.")
                else:
                    raise HTTPError(
                        "Unauthorized. This video may be subscriber-only. See docs:\n"
                        "https://twitch-dl.bezdomni.net/commands/download.html#downloading-subscriber-only-vods"
                    )

            raise

    def _retrieve_or_create_stream(self, stream):
        stream, created = Stream.objects.get_or_create(
            stream_id=stream["id"])

        if created:
            print('Created stream', stream.id)

        return stream

    def _get_authorized_request(self, url):
        if url in self.stream_calls:
            return self.stream_calls[url]

        r = requests.get(url, headers={
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": "Bearer " + self.access_token
        })

        self.stream_calls[url] = r

        return r.json()['data']

    def _post_authorized_request(self, url, data=None, json=None, headers={}):
        headers['Client-ID'] = GQL_CLIENT_ID

        response = httpx.post(url, data=data, json=json, headers=headers)
        if response.status_code == 400:
            data = response.json()
            raise Exception(data["message"])

        response.raise_for_status()

        return response

    def gql_post(self, query):
        url = "https://gql.twitch.tv/gql"
        response = self._post_authorized_request(url, data=query).json()

        if "errors" in response:
            raise Exception(response["errors"])

        return response

    def gql_query(self, query, headers={}):
        url = "https://gql.twitch.tv/gql"
        response = self._post_authorized_request(
            url, json={"query": query}, headers=headers).json()

        if "errors" in response:
            raise Exception(response["errors"])

        return response

    def get_user(self, user_id):
        url = f"https://api.twitch.tv/helix/users?id={user_id}"

        return self._get_authorized_request(url)[0]

    def get_game_id(self, game_name):
        query = """
        {{
            game(name: "{}") {{
                id
            }}
        }}
        """

        response = self.gql_query(query.format(game_name.strip()))
        game = response["data"]["game"]

        if game:
            return game["id"]

        return None

    def get_game(self, game_id):
        url = f"https://api.twitch.tv/helix/games?id={game_id}"

        return self._get_authorized_request(url)[0]

    def get_tag(self, tag_id):
        url = f"https://api.twitch.tv/helix/tags/streams?tag_id={tag_id}"

        return self._get_authorized_request(url)

    def get_category(self, category_id):
        url = f"https://api.twitch.tv/helix/streams?first=100&game_id={category_id}"

        return self._get_authorized_request(url)

    def get_streams(self):
        streams = []

        # Get all the streams from the categories and tags.
        for category in self.CATEGORIES:
            streams.append(self.get_category(category))

        # flatten streams array
        return [item for sublist in streams for item in sublist]

    def get_live_streams(self, streams=None):
        if streams is None:
            streams = self.get_streams()

        live_streams = []

        for stream in streams:
            if stream["type"] == "live":
                live_streams.append(stream)

        return live_streams

    def get_filtered_streams(self, streams=None, tags=TAGS, max_viewers=-1):
        if streams is None:
            streams = self.get_live_streams()

        filtered_streams = []

        for stream in streams:
            viewer_conforming = stream["viewer_count"] <= max_viewers or max_viewers == -1
            tag_collision = any(tag in stream["title"] for tag in tags)

            if viewer_conforming and tag_collision:
                filtered_streams.append(stream)

        return filtered_streams

    def get_clip(self, clip_id):
        query = """
        {{
            clip(slug: "{}") {{
                {fields}
            }}
        }}
        """

        response = self.gql_query(query.format(
            clip_id, fields=self.CLIP_FIELDS))
        return response["data"]["clip"]

    def get_clip_access_token(self, slug):
        """
        Retrieves the specific access token that is used to read a clip.
        """
        query = """
        {{
            "operationName": "VideoAccessToken_Clip",
            "variables": {{
                "slug": "{slug}"
            }},
            "extensions": {{
                "persistedQuery": {{
                    "version": 1,
                    "sha256Hash": "36b89d2507fce29e5ca551df756d27c1cfe079e2609642b4390aa4c35796eb11"
                }}
            }}
        }}
        """

        response = self.gql_post(query.format(slug=slug).strip())
        return response["data"]["clip"]

    def get_clips(self, user_name, period, limit, after=None):
        """
        List channel clips.

        At the time of writing this:
        * filtering by game name returns an error
        * sorting by anything but VIEWS_DESC or TRENDING returns an error
        * sorting by VIEWS_DESC and TRENDING returns the same results
        * there is no totalCount
        """
        query = """
        {{
        user(login: "{user_name}") {{
            clips(first: {limit}, after: "{after}", criteria: {{ period: {period}, sort: VIEWS_DESC }}) {{
            pageInfo {{
                hasNextPage
                hasPreviousPage
            }}
            edges {{
                cursor
                node {{
                {fields}
                }}
            }}
            }}
        }}
        }}
        """

        query = query.format(
            user_name=user_name,
            after=after if after else "",
            limit=limit,
            period=period.upper(),
            fields=self.CLIP_FIELDS
        )

        response = self.gql_query(query)
        user = response["data"]["user"]

        if not user:
            raise HTTPError(f"Channel {user_name} not found")

        return response["data"]["user"]["clips"]

    def get_video(self, video_id):
        query = """
        {{
            video(id: "{video_id}") {{
                {fields}
            }}
        }}
        """

        query = query.format(video_id=video_id, fields=self.VIDEO_FIELDS)

        response = self.gql_query(query)
        return response["data"]["video"]

    def get_videos(self, user_name, limit, sort, type="archive", game_ids=[], after=None):
        query = """
        {{
            user(login: "{user_name}") {{
                videos(
                    first: {limit},
                    type: {type},
                    sort: {sort},
                    after: "{after}",
                    options: {{
                        gameIDs: {game_ids}
                    }}
                ) {{
                    totalCount
                    pageInfo {{
                        hasNextPage
                    }}
                    edges {{
                        cursor
                        node {{
                            {fields}
                        }}
                    }}
                }}
            }}
        }}
        """

        query = query.format(
            user_name=user_name,
            game_ids=game_ids,
            after=after if after else "",
            limit=limit,
            sort=sort.upper(),
            type=type.upper(),
            fields=self.VIDEO_FIELDS
        )

        response = self.gql_query(query)

        if not response["data"]["user"]:
            raise HTTPError("Channel {} not found".format(user_name))

        return response["data"]["user"]["videos"]

    def get_playlists(self, video_id, access_token):
        url = f"http://usher.twitch.tv/vod/{video_id}"

        r = httpx.get(url, params={
            "nauth": access_token["value"],
            "nauthsig": access_token["signature"],
            "allow_audio_only": "true",
            "allow_source": "true",
            "player": "twitchweb"
        })

        r.raise_for_status()

        return r.content.decode('utf-8')

    def _clips_generator(self, channel_id, period, limit, clips):
        print('in generator')

        for clip in clips["edges"]:
            if limit < 1:
                return
            yield clip["node"]
            limit -= 1

        has_next = clips["pageInfo"]["hasNextPage"]
        if limit < 1 or not has_next:
            return

        req_limit = min(limit, 100)
        cursor = clips["edges"][-1]["cursor"]

        clips = self.get_clips(channel_id, period, req_limit, cursor)
        yield from self._clips_generator(clips, limit)

    def clips_generator(self, channel_id, period, limit):
        def _generator(clips, limit):
            for clip in clips["edges"]:
                if limit < 1:
                    return
                yield clip["node"]
                limit -= 1

            has_next = clips["pageInfo"]["hasNextPage"]
            if limit < 1 or not has_next:
                return

            req_limit = min(limit, 100)
            cursor = clips["edges"][-1]["cursor"]
            clips = self.get_clips(channel_id, period, req_limit, cursor)
            yield from _generator(clips, limit)

        req_limit = min(limit, 100)
        clips = self.get_clips(channel_id, period, req_limit)
        return list(_generator(clips, limit))

    def clips_generator_old(self, channel_id, period, limit):
        cursor = ""
        while True:
            clips = self.get_clips(
                channel_id, period, limit, after=cursor)

            if not clips["edges"]:
                break

            has_next = clips["pageInfo"]["hasNextPage"]
            cursor = clips["edges"][-1]["cursor"] if has_next else None

            yield clips, has_next

            if not cursor:
                break

    def videos_generator(self, channel_id, max_videos, sort, type, game_ids=[]):
        def _generator(videos, max_videos):
            for video in videos["edges"]:
                if max_videos < 1:
                    return
                yield video["node"]
                max_videos -= 1

            has_next = videos["pageInfo"]["hasNextPage"]
            if max_videos < 1 or not has_next:
                return

            limit = min(max_videos, 100)
            cursor = videos["edges"][-1]["cursor"]
            videos = self.get_videos(
                channel_id, limit, sort, type, game_ids, cursor)
            yield from _generator(videos, max_videos)

        limit = min(max_videos, 100)
        videos = self.get_videos(channel_id, limit, sort, type, game_ids)
        return videos["totalCount"], _generator(videos, max_videos)
