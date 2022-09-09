import asyncio
import httpx
import m3u8
import os
import re

from os import path
from pathlib import Path
from urllib.parse import urlparse, urlencode

from streams import twitch, utils
from .http import download_all

CHUNK_SIZE = 1024
CONNECT_TIMEOUT = 5
RETRY_COUNT = 5


class DownloadFailed(Exception):
    pass


def _download(url, path):
    size = 0
    with httpx.stream("GET", url, timeout=CONNECT_TIMEOUT) as response:
        with open(path, "wb") as target:
            for chunk in response.iter_bytes(chunk_size=CHUNK_SIZE):
                target.write(chunk)
                size += len(chunk)

    return size


def download_file(url: str, path: str, retries: int = RETRY_COUNT):
    if os.path.exists(path):
        from_disk = True
        return (os.path.getsize(path), from_disk)

    from_disk = False
    for _ in range(retries):
        try:
            return (_download(url, path), from_disk)
        except httpx.RequestError:
            pass

    raise DownloadFailed(":(")


class DownloadManager:
    def __init__(self):
        self.twitch_manager = twitch.TwitchManager()
        super().__init__()

    def _parse_playlists(self, playlists_m3u8):
        playlists = m3u8.loads(playlists_m3u8)

        for p in sorted(playlists.playlists, key=lambda p: p.stream_info.resolution is None):
            if p.stream_info.resolution:
                name = p.media[0].name
                description = "x".join(str(r)
                                       for r in p.stream_info.resolution)
            else:
                name = p.media[0].group_id
                description = None

            yield name, description, p.uri

    def _get_playlist_by_name(self, playlists, quality):
        if quality == "source":
            _, _, uri = playlists[0]
            return uri

        for name, _, uri in playlists:
            if name == quality:
                return uri

        available = ", ".join([name for (name, _, _) in playlists])
        msg = "Quality '{}' not found. Available qualities are: {}".format(
            quality, available)

        raise Exception(msg)

    def _video_target_filename(self, video, args):
        date, time = video['publishedAt'].split("T")
        game = video["game"]["name"] if video["game"] else "Unknown"

        subs = {
            "channel": video["creator"]["displayName"],
            "channel_login": video["creator"]["login"],
            "date": date,
            "datetime": video["publishedAt"],
            "format": args["format"],
            "game": game,
            "game_slug": utils.slugify(game),
            "id": video["id"],
            "time": time,
            "title": utils.titlify(video["title"]),
            "title_slug": utils.slugify(video["title"]),
        }

        try:
            return args["output"].format(**subs)
        except KeyError as e:
            supported = ", ".join(subs.keys())
            raise Exception(
                "Invalid key {} used in --output. Supported keys are: {}".format(e, supported))

    def _clip_target_filename(self, clip, args):
        date, time = clip["createdAt"].split("T")
        game = clip["game"]["name"] if clip["game"] else "Unknown"

        url = clip["videoQualities"][0]["sourceURL"]
        _, ext = path.splitext(url)
        ext = ext.lstrip(".")

        subs = {
            "channel": clip["broadcaster"]["displayName"],
            "channel_login": clip["broadcaster"]["login"],
            "date": date,
            "datetime": clip["createdAt"],
            "format": ext,
            "game": game,
            "game_slug": utils.slugify(game),
            "id": clip["id"],
            "slug": clip["slug"],
            "time": time,
            "title": utils.titlify(clip["title"]),
            "title_slug": utils.slugify(clip["title"]),
        }

        try:
            return args['output'].format(**subs)
        except KeyError as e:
            supported = ", ".join(subs.keys())
            raise Exception(
                "Invalid key {} used in --output. Supported keys are: {}".format(e, supported))

    def _get_vod_paths(self, playlist, start, end):
        """Extract unique VOD paths for download from playlist."""
        files = []
        vod_start = 0
        for segment in playlist.segments:
            vod_end = vod_start + segment.duration

            # `vod_end > start` is used here becuase it's better to download a bit
            # more than a bit less, similar for the end condition
            start_condition = not start or vod_end > start
            end_condition = not end or vod_start < end

            if start_condition and end_condition and segment.uri not in files:
                files.append(segment.uri)

            vod_start = vod_end

        return files

    def _crete_temp_dir(self, base_uri: str) -> str:
        """Create a temp dir to store downloads if it doesn't exist."""
        path = urlparse(base_uri).path.lstrip("/")

        temp_dir = Path("tmp", path)

        temp_dir.mkdir(parents=True, exist_ok=True)
        return str(temp_dir)

    def download(self, args):
        for video_id in args.videos:
            self.download_one(video_id, args)

    def download_one(self, video: str, args):
        video_id = utils.parse_video_identifier(video)
        if video_id:
            return self._download_video(video_id, args)

        clip_slug = utils.parse_clip_identifier(video)
        if clip_slug:
            return self._download_clip(clip_slug, args)

        raise Exception("Invalid input: {}".format(video))

    def _get_clip_url(self, clip, quality):
        qualities = clip["videoQualities"]

        # Quality given as an argument
        if quality:
            if quality == "source":
                return qualities[0]["sourceURL"]

            selected_quality = quality.rstrip("p")  # allow 720p as well as 720
            for q in qualities:
                if q["quality"] == selected_quality:
                    return q["sourceURL"]

            available = ", ".join([str(q["quality"]) for q in qualities])
            msg = "Quality '{}' not found. Available qualities are: {}".format(
                quality, available)
            raise Exception(msg)

        # Auto quality
        selected_quality = qualities[0]
        return selected_quality["sourceURL"]

    def get_clip_authenticated_url(self, slug, quality):
        access_token = self.twitch_manager.get_clip_access_token(slug)

        if not access_token:
            raise Exception(
                "Access token not found for slug '{}'".format(slug))

        url = self._get_clip_url(access_token, quality)

        query = urlencode({
            "sig": access_token["playbackAccessToken"]["signature"],
            "token": access_token["playbackAccessToken"]["value"],
        })

        return "{}?{}".format(url, query)

    def _download_clip(self, slug: str, args) -> None:
        clip = self.twitch_manager.get_clip(slug)
        game = clip["game"]["name"] if clip["game"] else "Unknown"

        if not clip:
            raise Exception("Clip '{}' not found".format(slug))

        target = self._clip_target_filename(clip, args)

        if not args["overwrite"] and path.exists(target):
            response = input("File exists. Overwrite? [Y/n]: ")
            if response.lower().strip() not in ["", "y"]:
                raise Exception("Aborted")
            args["overwrite"] = True

        url = self.get_clip_authenticated_url(slug, args["quality"])

        download_file(url, target)

    def _download_video(self, video_id, args) -> None:
        if args['start'] and args['end'] and args['end'] <= args['start']:
            raise Exception("End time must be greater than start time")

        video = self.twitch_manager.get_video(video_id)

        if not video:
            raise Exception("Video {} not found".format(video_id))

        target = self._video_target_filename(video, args)

        if not args["overwrite"] and path.exists(target):
            response = input("File exists. Overwrite? [Y/n]: ")
            if response.lower().strip() not in ["", "y"]:
                raise Exception("Aborted")
            args["overwrite"] = True

        access_token = self.twitch_manager.get_gql_access_token(
            video_id, auth_token=args["auth_token"])

        playlists_m3u8 = self.twitch_manager.get_playlists(
            video_id, access_token)
        playlists = list(self._parse_playlists(playlists_m3u8))
        playlist_uri = (self._get_playlist_by_name(playlists, args["quality"]))

        response = httpx.get(playlist_uri)
        response.raise_for_status()
        playlist = m3u8.loads(response.text)

        base_uri = re.sub("/[^/]+$", "/", playlist_uri)
        target_dir = self._crete_temp_dir(base_uri)
        vod_paths = self._get_vod_paths(playlist, args["start"], args["end"])

        sources = [base_uri + path for path in vod_paths]
        targets = [os.path.join(target_dir, "{:05d}.ts".format(
            k)) for k, _ in enumerate(vod_paths)]
        asyncio.run(download_all(sources, targets,
                    args["max_workers"], rate_limit=args["rate_limit"]))
