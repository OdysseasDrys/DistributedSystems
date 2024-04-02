from time import time
import hashlib # maybe change to Crypto.Hash instead
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
    - capacity: the capacity of the block
    - fees: the fees of the block
    """

    def __init__(self, index, previous_hash, capacity):
        self.index = index
        self.timestamp = time()
        self.transactions = []
        self.validator = None
        self.previous_hash = previous_hash
        self.current_hash = None
        self.capacity = capacity
        self.fees = 0

    def add_transaction(self, transaction):
        """Add a transaction to the block"""
        if len(self.transactions) < self.capacity:
            self.transactions.append(transaction)
            return True
        else:
            return False

    def calculate_hash(self):
        """Calculate the hash of the block"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'validator': self.validator,
            'previous_hash': self.previous_hash,
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    