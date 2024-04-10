from blockchain import Blockchain
from block import Block
from wallet import Wallet
from transaction import Transaction
import requests
import pickle
import random
import jsonpickle
from threading import Lock,Thread

class Node:
    """
    A node in the network.

    Attributes:
        id (int): the id of the node.
        balance (int): the bcc coins of the node.
        wallet (Wallet): the wallet of the node. 
        blockchain (Blockchain): the blockchain of the node.
        current_block (Block): the block that the node is fills with transactions.
        capacity (int): max number of transactions in each block.
        state (dict): list of information about other nodes
                     (id, ip, port, public_key, balance, stake_amount).
        stake_amount (int): the amount of BCC that the node has staked.        
        
    """

    def __init__(self):
        """Initializes a Node."""
        self.id = None
        self.balance = 0
        self.generate_wallet()
        self.chain_lock = Lock()
        self.filter_lock = Lock()
        self.block_lock = Lock()
        self.blockchain = Blockchain()
        self.current_block = None
        self.capacity = None
        self.state = []
        self.stake_amount = 0
        
    def __str__(self): 
        return str(self.__class__) + ": " + str(self.__dict__)
    
    def generate_wallet(self):
        """Generate a wallet for the node."""
        self.wallet= Wallet()
    
    def create_new_block(self):
        """Creates a new block for the blockchain."""
        if len(self.blockchain.blocks) == 0:
            index = 0
            previous_hash = 1
            self.current_block = Block(index, previous_hash, self.capacity)
        else:
            index = len(self.blockchain.blocks) + 1
            previous_hash= self.blockchain.blocks[-1].calculate_hash()
            self.current_block = Block(index, previous_hash, self.capacity)
        return self.current_block

    def create_transaction(self, receiver_address, type_of_transaction, amount, message):
        """Create a transaction for the node."""
        # # In case we dont take fees for the starting transactions
        # if self.sender_address == 0 and (self.wallet.nonce in {1,2,3,4}):
        #     self.wallet.nonce += 1
        #     transaction = Transaction(self.wallet.public_key, receiver_address, type_of_transaction, amount, None, self.wallet.nonce)
        #     self.balance -= amount

        if receiver_address != 0:
            if type_of_transaction == 'first':
                self.wallet.nonce += 1
                transaction = Transaction(self.wallet.public_key, receiver_address, type_of_transaction, amount, "-", self.wallet.nonce)
                print("Transaction initialized", jsonpickle.encode(transaction))
                transaction.sign_transaction(self.wallet.private_key)
                self.balance -= amount
            if type_of_transaction == 'coins':
                print("--start")
                fee = 0.03*amount
                if (self.balance >= (amount+fee)):
                    self.wallet.nonce += 1
                    transaction = Transaction(self.wallet.public_key, receiver_address, type_of_transaction, amount, "-", self.wallet.nonce)
                    print("Transaction initialized", jsonpickle.encode(transaction))
                    transaction.sign_transaction(self.wallet.private_key)
                    self.current_block.fees += fee
                    self.balance -= (fee+amount)
                    print("---finish")
            if type_of_transaction == 'message':
                fee = len(message)
                
                if (self.balance >= fee):
                    transaction = Transaction(self.wallet.public_key, receiver_address, type_of_transaction, 0, message, self.wallet.nonce)
                    print("Transaction initialized", jsonpickle.encode(transaction))
                    transaction.sign_transaction(self.wallet.private_key)
                    self.current_block.fees += fee
                    self.balance -= fee
                    self.wallet.nonce += 1
              
        else: #in case it is a stake transaction 
            if amount > self.stake_amount:
                self.wallet.nonce += 1
                transaction = Transaction(self.wallet.public_key, receiver_address, type_of_transaction, amount, "-", self.wallet.nonce)
                print("Transaction initialized", jsonpickle.encode(transaction))
                transaction.sign_transaction(self.wallet.private_key)
                self.balance -= amount
                
            elif amount < self.stake_amount:
                self.wallet.nonce += 1
                transaction = Transaction(receiver_address, self.wallet.public_key, type_of_transaction, amount, "-", self.wallet.nonce)
                print("Transaction initialized", jsonpickle.encode(transaction))
                transaction.sign_transaction(self.wallet.private_key)
                self.balance += amount
                
        # print("Transaction initialized", transaction)
        

        return self.broadcast_transaction(transaction)
              
  
    def stake(self, amount):
        """Set the node's stake."""
        if self.stake_amount == amount:
            print("Amount already staked")
            return False
        elif self.balance >= amount:
            self.create_transaction(self.wallet.public_key, 0, 'coins', amount, None)
            return True
        else:
            print("Not enough BCC")
            return False

    def broadcast_transaction(self, transaction):
        """Broadcast a transaction

        The transaction is broadcasted to all other nodes, the nodes check
        the state to verify that the node that initiated the transaction
        has the available tokens to do the transaction
        If the transaction is realisable, the nodes respond with 200 OK.
        """
        flag=True
        for node in self.state:
            if node['id'] != self.id:
                try:
                    address = 'http://' + node['ip'] + ':' + node['port']
                    response = requests.post(address + '/validate_transaction',
                                             data=pickle.dumps(transaction))
                    if response.status_code != 200:
                        print(f'broadcast: Request "{node["ip"]}/{node["port"]}" failed')


                except requests.exceptions.Timeout:
                    print(f'broadcast: Request "{node["ip"]}/{node["port"]}" timed out')
                    pass
        
        for node in self.state:
            if node['id'] != self.id:
                try:
                    address = 'http://' + node['ip'] + ':' + node['port']
                    response = requests.post(address + '/get_transaction',
                                             data=pickle.dumps(transaction))
                    if response.status_code != 200:
                        flag=False
                        print(f'broadcast: Request "{node["ip"]}/{node["port"]}" failed')
                    
    
                except requests.exceptions.Timeout:
                    print(f'broadcast: Request "{node["ip"]}/{node["port"]}" timed out')
                    pass

        #if not flag:
        if not self.add_transaction_to_block(transaction): ##OXI AFTO
            validator = self.proof_of_stake()
            print("---- validator id" , validator)
            self.validation_sequence(validator)  
        
        return True

    def validation_sequence(self, validator):

        self.state = self.calculate_state()
        self.current_block.state = self.state

        if self.id == validator:         
            responses = []
            # broadcasted = False
            broadcasted = True
            for node in self.state:
                if node["id"]!=self.id:
                    response = self.current_block.broadcast_block(node["ip"], node["port"])
                    responses.append(response)
            
            for res in responses:
                # if res == 200:
                #     broadcasted = True  
                if res != 200:
                    broadcasted = False
                    break          
            if broadcasted:
                self.balance += self.current_block.fees
                self.blockchain.add_block(self.current_block)            
                self.create_new_block()
        return True
    
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


    def validate_transaction(self, transaction):
        """Validates an incoming transaction.

        The validation consists of:
        - Check that the signature matches
        - Check the the wallet of the sender has enough BCC.
        """

        if not transaction.verify_signature():
            return False

        for node in self.state:
            if node['public_key'] == transaction.sender_address:
                if transaction.type_of_transaction == "first":
                    full_amount = transaction.amount
                elif transaction.type_of_transaction == "coins":                
                    full_amount = 1.03*transaction.amount 
                if transaction.type_of_transaction == "message":
                    full_amount = len(transaction.message)
                if node['balance'] >= full_amount:
                    return True
        return False
    
    def calculate_state(self):
        # print(self.blockchain)
        """Validates the blockchain by checking all the transactions inside all the blocks"""
        for block in self.blockchain.blocks:
            for transaction in block.transactions:
                for node in self.state:
                    if transaction.type_of_transaction == "coins":
                        if transaction.sender_address == node["public_key"]:
                            node["balance"] -= 1.03*transaction.amount
                        
                        if transaction.receiver_address == node["public_key"]:
                            node["balance"] += transaction.amount
                    if transaction.type_of_transaction == "message":
                        amount = len(transaction.message)
                        if transaction.sender_address == node["public_key"]:
                            node["balance"] -= amount
        return self.state

                        

    def add_transaction_to_block(self, transaction):
        
        #if node sender or receiver add transaction 
        if (transaction.sender_address == self.wallet.public_key) or (transaction.receiver_address == self.wallet.public_key):
            # if transaction.type_of_transaction == "message":
            #     fee = len(transaction.message)
            # elif transaction.type_of_transaction == "coins":
            #     fee = 1.03*transaction.amount
            # elif transaction.type_of_transaction == "first":
            #     fee = 0
            # transaction.fee = fee
            self.wallet.add_transaction_to_wallet(transaction)
            
        # Update the balance of the recipient and the sender.
        if self.current_block is None:
            self.current_block = self.create_new_block()

        if len(self.current_block.transactions) < self.capacity:
            for node in self.state:            
                if transaction.type_of_transaction == 'message':
                    fee = len(transaction.message)
                    if node['public_key'] == transaction.sender_address:
                        node['balance'] -= fee
                        break
                if node['public_key'] == transaction.sender_address:
                    node['balance'] -= transaction.amount
                    continue
                if node['public_key'] == transaction.receiver_address:
                    node['balance'] += transaction.amount
                    continue
            return True
        else: 
            # validator = self.proof_of_stake()
            # self.validation_sequence(validator) 
            return False

    def proof_of_stake(self):
            random.seed(self.current_block.previous_hash)
            stakes = [node['stake'] for node in self.state]
            total_stake = sum(stakes)
            if total_stake == 0:
                return random.choice(self.state)['id']  # Fallback if no stakes are present

            summ = 0
            number = random.randint(0,total_stake)
            for i in enumerate(stakes):
                summ += stakes[i]
                if number <= summ:
                    return self.state[i]['id']
                
    def share_state(self, node):
        """Shares the node's ring (neighbor nodes) to a specific node.

        This function is called for every newcoming node in the blockchain.
        """

        address = 'http://' + node['ip'] + ':' + node['port']
        requests.post(address + '/get_state',
                      data=pickle.dumps(self.state))
        
    def share_blockchain(self, node):
        """Shares the node's current blockchain to a specific node.
        """

        address = 'http://' + node['ip'] + ':' + node['port']
        requests.post(address + '/get_blockchain', data=pickle.dumps(self.blockchain))
        # requests.post(address + '/get_blockchain', data=jsonpickle.encode(self.blockchain))


        