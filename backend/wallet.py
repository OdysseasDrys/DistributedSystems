import binascii
import jsonpickle

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

        #random_gen = Crypto.Random.new().read
        #private_key = RSA.generate(1024, random_gen)
        #public_key = private_key.publickey()
        self.nonce = 0

        # Save keys as hex strings
        #self.private_key = binascii.hexlify(private_key.export_key(format='DER')).decode('ascii')
        #self.public_key = binascii.hexlify(public_key.export_key(format='DER')).decode('ascii')
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
    
    
    def get_stake_balance(self):
        """
        Get the stake balance of the wallet
        """
        stake_balance = 0
        for transaction in self.transactions:
            if transaction.receiver_address == 0 and transaction.nonce != 0: # to avoid first transaction
                stake_balance = 0
                stake_balance += transaction.amount
        return abs(stake_balance)
    
    def get_balance(self):
        """
        Get the balance of the wallet
        """
        balance = 0
        staked_balance = self.get_stake_balance()
        for transaction in self.transactions:
            print("---",jsonpickle.encode(transaction))
            # print("--- TO KLEIDI ---",self.public_key)
            if transaction.sender_address != 0:
                if transaction.sender_address == self.public_key:
                    balance -= transaction.amount
                elif transaction.receiver_address == self.public_key:
                    balance += transaction.amount
        return balance - abs(staked_balance)