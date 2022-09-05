from django.test import TestCase

from .keys import KeyManager

class KeyManagerTestCase(TestCase):
    def setUp(self):
        self.key_manager = KeyManager()

    def test_sync_key(self):
        pass

    def test_is_private_key(self):
        key = "3f6e3d2c2f1c1f0e0d0c0b0a090807060504030201000f0e0d0c0b0a09080706"
        
        self.assertTrue(self.key_manager.is_private_key(key))