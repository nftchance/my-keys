"""
Key Manager is a class that takes a supplied key and determines if it is a 
valid private key for a cryptocurrency wallet.
"""

import time

from django.conf import settings

from web3 import Web3

from repos.models import RepoKey


class KeyManager:
    TYPES = {
        'ETH': None,
    }

    def __init__(self) -> None:
        self.TYPES['ETH'] = Web3(Web3.HTTPProvider(
            f'https://eth-mainnet.alchemyapi.io/v2/{settings.ALCHEMY_KEY}'))

    def start(self):
        print("KeyManager started")

        while True:
            keys = RepoKey.objects.filter(synced=False)

            if keys.exists():
                for key in keys:
                    self.sync_key(key)
            else:
                time.sleep(600)

    def sync_key(self, key):
        if self.is_address(key.key):
            key.address = self.get_checksum_address(key.key)
        elif self.is_private_key(key.key):
            key.is_private_key = True
            key.address = self.get_address(key.key)

        if key.address and key.address != '':
            key.balance = self.get_balance(key.address)

        key.synced = True
        key.save()

    def sync_keys(self, keys):
        for key in keys:
            self.sync_key(key)

    def is_private_key(self, key, type='ETH') -> bool:
        try:
            self.get_address(key, type)
            return True
        except Exception as e:
            return False

    def is_address(self, address, type='ETH') -> bool:
        return self.TYPES[type].isAddress(address)

    def get_checksum_address(self, address, type='ETH') -> str:
        return self.TYPES[type].toChecksumAddress(address)

    def get_address(self, key, type='ETH') -> str:
        return self.get_checksum_address(self.TYPES[type].eth.account.privateKeyToAccount(key).address)

    def get_balance(self, key, type='ETH') -> str:
        return self.TYPES[type].eth.getBalance(key)
