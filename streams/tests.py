from django.test import TestCase

from streams.twitch import TwitchManager

class TwitchTestCase(TestCase):
    def setUp(self):
        self.twitch_manager = TwitchManager()

    def test_get_user(self):
        user = self.twitch_manager.get_user("44322889")

        self.assertEqual(user["data"][0]["id"], "44322889")

    def test_get_game(self):
        game = self.twitch_manager.get_game("21779")

        self.assertEqual(game["data"][0]["id"], "21779")

    def test_get_tag(self):
        tag = self.twitch_manager.get_tag("6ea6bca4-4712-4ab9-a906-e3336a9d8039")

        self.assertEqual(tag["data"][0]["tag_id"], "6ea6bca4-4712-4ab9-a906-e3336a9d8039")

    def test_get_category(self):
        category = self.twitch_manager.get_category("509658")

        self.assertEqual(category["data"][0]["id"], "509658")

    def test_get_vods(self):
        streams = self.twitch_manager.get_vods("44322889")

        print(streams)

        self.assertEqual(streams["data"][0]["user_id"], "44322889")

    def test_get_streams(self):
        streams = self.twitch_manager.get_streams()

        self.assertNotEqual(len(streams), 0)