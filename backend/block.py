from time import time
import hashlib # maybe change to Crypto.Hash instead
import json
import pickle
import responses
import requests

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
        print("---", self.capacity)
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
    
    def broadcast_block(self, ip, port):
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'validator': self.validator,
            'previous_hash': self.previous_hash,
            'capacity': self.capacity,
            'fees': self.fees
        }
        address = 'http://' + ip + ':' + port + '/get_block'
        # Serialize the block_data dictionary to bytes using pickle.dumps
        block_bytes = pickle.dumps(block_data)
        # Send the pickled data as the payload
        response = requests.post(address, data=block_bytes)
        return response.status_code
    