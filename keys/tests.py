from django.test import TestCase

from repos.models import RepoKey

from .keys import KeyManager


class KeyManagerTestCase(TestCase):
    def setUp(self):
        self.key_manager = KeyManager()

    def test_sync_key(self):
        repo_key, created = RepoKey.objects.get_or_create(
            key="0x62180042606624f02D8A130dA8A3171e9b33894d",
        )

        self.key_manager.sync_key(repo_key)

        self.assertTrue(repo_key.balance > 0)

    def test_is_private_key(self):
        key = "3f6e3d2c2f1c1f0e0d0c0b0a090807060504030201000f0e0d0c0b0a09080706"

        self.assertTrue(self.key_manager.is_private_key(key))

    def test_is_address(self):
        address = "0x0f0e0d0c0b0a090807060504030201000f0e0d0c"

        self.assertTrue(self.key_manager.is_address(address))

    def test_get_checksum_adress(self):
        address = "0x0f0e0d0c0b0a090807060504030201000f0e0d0c"
        checksum_address = "0x0f0e0D0c0B0a090807060504030201000f0E0D0c"

        self.assertEqual(checksum_address,
                         self.key_manager.get_checksum_address(address))

    def test_get_address(self):
        key = "3f6e3d2c2f1c1f0e0d0c0b0a090807060504030201000f0e0d0c0b0a09080706"

        address = "0xE3398d511DA9e13aB73AFa817047F36d3eFefAab"

        self.assertEqual(address, self.key_manager.get_address(key))

    def test_get_balance(self):
        address = "0x62180042606624f02D8A130dA8A3171e9b33894d"

        balance = self.key_manager.get_balance(address)

        self.assertTrue(balance > 0)
