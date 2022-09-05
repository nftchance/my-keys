"""
Key Manager is a class that takes a supplied key and determines if it is a 
valid private key for a cryptocurrency wallet.
"""

import os 

from web3 import Web3

ALCHEMY_KEY = os.environ.get('ALCHEMY_KEY')

class KeyManager:
    TYPES = { 
        'ETH': None,
    }

    def __init__(self) -> None:
        self.TYPES['ETH'] = Web3(Web3.HTTPProvider(self.TYPES['ETH']))

    def is_private_key(self, key, type='ETH'):
        try:
            self.get_address(key, type)
            return True
        except:
            return False

    def is_address(self, address, type='ETH'):
        return self.TYPES[type].isAddress(address)

    def get_address(self, key, type='ETH'):
        return self.TYPES[type].eth.account.privateKeyToAccount(key).address

    def get_balance(self, key, type='ETH'):
        return self.TYPES[type].eth.getBalance(self.get_address(key, type))
    