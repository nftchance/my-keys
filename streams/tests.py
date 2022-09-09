from django.test import TestCase

from streams.download import DownloadManager
from streams.twitch import TwitchManager


class TwitchTestCase(TestCase):
    def setUp(self):
        self.twitch_manager = TwitchManager()

    def test_get_user(self):
        user = self.twitch_manager.get_user("44322889")
        self.assertEqual(user["id"], "44322889")

    def test_get_game_id(self):
        game_id = self.twitch_manager.get_game_id("Science & Technology")

        self.assertEqual(game_id, "509670")

        game_id = self.twitch_manager.get_game_id(
            "Software and Game Development")

        self.assertEqual(game_id, "1469308723")

    def test_get_game(self):
        game = self.twitch_manager.get_game("21779")

        self.assertEqual(game["id"], "21779")

    def test_get_tag(self):
        streams = self.twitch_manager.get_tag(
            "6ea6bca4-4712-4ab9-a906-e3336a9d8039")
        self.assertEqual(streams[0]["tag_id"],
                         "6ea6bca4-4712-4ab9-a906-e3336a9d8039")

    def test_get_category(self):
        streams = self.twitch_manager.get_category("509658")
        self.assertEqual(streams[0]["game_id"], "509658")

    def test_get_streams(self):
        streams = self.twitch_manager.get_streams()

        self.assertNotEqual(len(streams), 0)

    def test_get_live_streams(self):
        streams = self.twitch_manager.get_live_streams()

        self.assertNotEqual(len(streams), 0)

    def test_get_filtered_steams(self):
        streams = self.twitch_manager.get_filtered_streams()

        self.assertNotEqual(len(streams), None)

    def test_get_clip(self):
        clip = self.twitch_manager.get_clip(
            "PerfectBitterBillBibleThump-1ao_vXD0XXBRUbe0")

        self.assertEqual(clip["id"], "586008086")

    def test_get_clips(self):
        # user id, period, limit
        clips = self.twitch_manager.get_clips("dallas", "LAST_MONTH", 10)

        self.assertNotEqual(len(clips), 0)

    def test_get_video(self):
        video = self.twitch_manager.get_video("1583537172")

        self.assertEqual(video["id"], "1583537172")

    def test_get_videos(self):
        videos = self.twitch_manager.get_videos("dallas", 10, "views")

        self.assertNotEqual(len(videos), 0)

    def test_get_playlists_with_no_auth_token(self):
        video_id = "1583537172"
        access_token = self.twitch_manager.get_gql_access_token(video_id)

        playlists = self.twitch_manager.get_playlists(video_id, access_token)

        self.assertNotEqual(len(playlists), 0)

    def test_clips_generator(self):
        generator = self.twitch_manager.clips_generator(
            "xqc", "LAST_MONTH", 10)
        self.assertNotEqual(len(generator), 0)

    def test_videos_generator(self):
        total_count, generator = self.twitch_manager.videos_generator(
            "xqc", 100, "views", "archive")
        self.assertNotEqual(len(generator), 0)


class DownloadManagerTestCase(TestCase):
    def setUp(self):
        self.download_manager = DownloadManager()

    def test_download(self):
        self.download_manager.download_one("1585732109", {
            "start": None,
            "end": None,
            "overwrite": True,
            "format": "mp4",
            "output": "{channel}_{id}.{format}",
            "auth_token": None,
            "quality": "source",
            "max_workers": 15,
            "rate_limit": None,
            "no_join": False
        })

    def test_download_clip(self):
        self.download_manager.download_one("StrangeSourCoyoteYee-Nc_r1-iZkEy_DfBe", {
            "start": None,
            "end": None,
            "overwrite": True,
            "format": "mp4",
            "output": "tmp/{channel}_{id}.{format}",
            "auth_token": None,
            "quality": "source",
            "max_workers": 15,
            "rate_limit": None,
            "no_join": False
        })
