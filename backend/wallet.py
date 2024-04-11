import binascii
import jsonpickle
import node
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

from json import JSONEncoder


class Wallet:
    """
    The wallet of a node in the network.
     public key: the public key of the node. Serves as the address of the node.
     private key: the private key of the node. Serves to sign transactions.
     transactions: the transactions of the node

    """

    def __init__(self):
        """Intialize the wallet"""
        random_gen = Crypto.Random.new().read
        key = RSA.generate(1024, random_gen)

        self.private_key = key.exportKey().decode('ISO-8859-1')
        self.public_key = key.publickey().exportKey().decode('ISO-8859-1')

        self.nonce = 0

        self.transactions = []

    def sign_transaction(self, transaction):
        """
        Sign a transaction with the private key
        """
        private_key = RSA.import_key(binascii.unhexlify(self.private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(json.dumps(transaction, sort_keys=True).encode('utf8'))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')

    def to_dict(self):
        """
        Convert the wallet to a dictionary
        """
        return {
            'public_key': self.public_key,
            'private_key': self.private_key,
            'transactions': self.transactions
        }
    
    def add_transaction_to_wallet(self, transaction):
        """
        Add a transaction to the wallet
        """
        
        self.transactions.append(transaction)

    
    def get_stake_balance(self,node):
        """
        Get the stake balance of the wallet
        """
        return node.stake_amount
    
    def get_balance(self,node):
        """
        Get the balance of the wallet
        """
        return node.balance #- abs(staked_balance)