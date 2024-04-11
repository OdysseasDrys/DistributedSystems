from time import time
import hashlib # maybe change to Crypto.Hash instead
import pickle
from timeit import default_timer as timer
from datetime import datetime

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
        
        self.timestamp = float(timer())
        # print("--BLOCK ",self.index, "WAS BORN ", datetime.now())
        self.transactions = []
        self.validator = None
        self.previous_hash = previous_hash
        self.current_hash = None
        self.capacity = capacity
        self.fees = 0
        self.time_of_death = 0
        

    def add_transaction(self, transaction):
        """Add a transaction to the block"""
        
        if len(self.transactions) < self.capacity:
            self.transactions.append(transaction)
            return True
        else:
            return False

    def calculate_hash(self):
        """Calculate the hash of the block"""
        block_dict = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'validator': self.validator,
            'previous_hash': self.previous_hash,
        }
        sorted_block_string = pickle.dumps(block_dict, protocol=0)
        return hashlib.sha256(sorted_block_string).hexdigest()
    
    