from time import time
import hashlib
import json

class Block(object):
    """
    Each block has:
    - index: number of the block
    - timestamp: timestamp the block was created
    - transactions: list of the transactions inside the block
    - validator: the public key of the block's validator
    - current_hash: the hash of the block
    - previous_hash: the hash of the previous block
    - capacity: how many transactions fit inside the block
    """

    def __init__(self, index, timestamp, transactions, validator, previous_hash, capacity):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.validator = validator
        self.previous_hash = previous_hash
        self.capacity = capacity
        self.current_hash = self.calculate_hash()

    def add_transaction(self, transaction):
        """Add a transaction to the block"""
        if len(self.transactions) < self.capacity:
            self.transactions.append(transaction)
            return True
        else:
            return False

    def calculate_hash(self):
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'validator': self.validator,
            'previous_hash': self.previous_hash,
            'capacity': self.capacity
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
