import binascii

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
    It contains:
     the public key of the node 
     the private key of the node
     the transactions of the node   

    """

    def __init__(self):
        random_gen = Crypto.Random.new().read
        private_key = RSA.generate(1024, random_gen)
        public_key = private_key.publickey()

        # Save keys as hex strings
        self.private_key = binascii.hexlify(private_key.export_key(format='DER')).decode('ascii')
        self.public_key = binascii.hexlify(public_key.export_key(format='DER')).decode('ascii')
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
    
    def add_transaction(self, transaction):
        """
        Add a transaction to the wallet
        """
        self.transactions.append(transaction)