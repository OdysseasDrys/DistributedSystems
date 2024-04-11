from blockchain import Blockchain
from block import Block
from wallet import Wallet
from transaction import Transaction
import requests
import pickle
import random
import jsonpickle
import time
from threading import Lock,Thread
import re
from timeit import default_timer as timer
import jsonpickle
from datetime import datetime

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
        self.validated_blocks = 0
        self.block_time = 0
        self.chain_lock = Lock()
        
    def __str__(self): 
        return str(self.__class__) + ": " + str(self.__dict__)
    
    def generate_wallet(self):
        """Generate a wallet for the node."""
        self.wallet= Wallet()
    
    def create_new_block(self):
        """Creates a new block for the blockchain."""
        if len(self.blockchain.blocks) == 0: #meaning genesis block

            index = 0
            previous_hash = 1
            self.current_block = Block(index, previous_hash, self.capacity)
            
        else:
            # print("2")
            index = len(self.blockchain.blocks)
            previous_hash= self.blockchain.blocks[-1].calculate_hash()
            self.current_block = Block(index, previous_hash, self.capacity)
            #send this current block to the other nodes
            # print("block index:", index)
            
        return self.current_block

    def create_transaction(self, receiver_address, type_of_transaction, amount, message):
        """Create a transaction for the node."""
        # # In case we dont take fees for the starting transactions
        # if self.sender_address == 0 and (self.wallet.nonce in {1,2,3,4}):
        #     self.wallet.nonce += 1
        #     transaction = Transaction(self.wallet.public_key, receiver_address, type_of_transaction, amount, None, self.wallet.nonce)
        #     self.balance -= amount
        # self.balance = self.wallet.get_balance()
        # print("Block Index ", self.current_block.index)
        # print("---self.balance", self.balance)
        if receiver_address != 0:
            
            if type_of_transaction == 'first':
                # print("--self.balance: ",self.balance," amount: ",amount)
                self.wallet.nonce += 1
                transaction = Transaction(self.wallet.public_key, receiver_address, type_of_transaction, amount, "-", self.wallet.nonce)
                #print("Transaction initialized", jsonpickle.encode(transaction))
                transaction.sign_transaction(self.wallet.private_key)
                self.balance -= amount
            if type_of_transaction == 'coins':
                # print("--self.balance: ",self.balance," amount: ",amount)
                #print("--start")
                fee = 0.03*amount
                # print("self.balance: ",self.balance," amount: ",amount," fee: ",fee)
                if (self.balance >= (amount+fee)):
                    
                    self.wallet.nonce += 1
                    transaction = Transaction(self.wallet.public_key, receiver_address, type_of_transaction, amount, "-", self.wallet.nonce)
                    #print("Transaction initialized", jsonpickle.encode(transaction))
                    transaction.sign_transaction(self.wallet.private_key)
                    
                    self.balance -= (fee+amount)
                    #print("---finish")
            if type_of_transaction == 'message':
                fee = len(message)
                
                if (self.balance >= fee):
                    transaction = Transaction(self.wallet.public_key, receiver_address, type_of_transaction, 0, message, self.wallet.nonce)
                    #print("Transaction initialized", jsonpickle.encode(transaction))
                    transaction.sign_transaction(self.wallet.private_key)
                    
                    self.balance -= fee
                    self.wallet.nonce += 1
              
        else: #in case it is a stake transaction 
            
                # print("---- amount and self.stake_amount: ", amount, self.stake_amount)
                if amount > self.stake_amount:
                    self.wallet.nonce += 1
                    amount_new = abs(amount - self.stake_amount)
                    transaction = Transaction(self.wallet.public_key, receiver_address, type_of_transaction, amount_new, "", self.wallet.nonce)
                    #print("Transaction initialized", jsonpickle.encode(transaction))
                    transaction.sign_transaction(self.wallet.private_key)
                    self.balance -= amount_new
                    self.stake_amount =  amount
                    self.state[self.id]["stake"] = amount
                    # print("---self.stake_amount for amount> ssa",self.stake_amount)
                    
                elif amount < self.stake_amount:
                    self.wallet.nonce += 1
                    amount_new = abs(self.stake_amount - amount)
                    transaction = Transaction(receiver_address, self.wallet.public_key, type_of_transaction, amount_new, "", self.wallet.nonce)
                    # print("EKANE TO TRANSACTION")
                    # print(jsonpickle.encode(transaction))
                    #print("Transaction initialized", jsonpickle.encode(transaction))
                    # transaction.sign_transaction(self.wallet.private_key)
                    # print("EKANE TO SIGN TRANSACTION")
                    self.balance += amount_new
                    self.stake_amount =  amount
                    self.state[self.id]["stake"] = amount
                    # print("---self.stake_amount for amount< ssa",self.stake_amount)
                
        # print("Transaction initialized", transaction)
        
        # print("--- receiver adress:", receiver_address)
        return self.broadcast_transaction(transaction)
              
  
    # def stake(self, amount):
    #     """Set the node's stake."""
    #     if self.stake_amount == amount:
    #         print("Amount already staked")
    #         return False
    #     elif self.balance > amount:
    #         self.create_transaction(self.wallet.public_key, 0, 'coins', amount, None)
    #         return True
    #     else:
    #         self.create_transaction(0,self.wallet.public_key, 'coins', amount, None)
    #         print("Not enough BCC")
    #         return False
    

    def broadcast_transaction(self, transaction):
        """Broadcast a transaction

        The transaction is broadcasted to all other nodes, the nodes check
        the state to verify that the node that initiated the transaction
        has the available tokens to do the transaction
        If the transaction is realisable, the nodes respond with 200 OK.
        """
        # flag=True
        # for node in self.state:
        #     if node['id'] != self.id:
        #         try:
        #             address = 'http://' + node['ip'] + ':' + node['port']
        #             response = requests.post(address + '/validate_transaction',
        #                                      data=pickle.dumps(transaction))
        #             if response.status_code != 200:
        #                 print(f'broadcast: Request "{node["ip"]}/{node["port"]}" failed')


        #         except requests.exceptions.Timeout:
        #             print(f'broadcast: Request "{node["ip"]}/{node["port"]}" timed out')
        #             pass
        
        # for node in self.state:
        #     if node['id'] != self.id:
        #         try:
        #             address = 'http://' + node['ip'] + ':' + node['port']
        #             response = requests.post(address + '/get_transaction',
        #                                      data=pickle.dumps(transaction))
        #             if response.status_code != 200:
        #                 flag=False
        #                 print(f'broadcast: Request "{node["ip"]}/{node["port"]}" failed')
                    
    
        #         except requests.exceptions.Timeout:
        #             print(f'broadcast: Request "{node["ip"]}/{node["port"]}" timed out')
        #             pass
        # print("EFTASE EDW")
        def thread_func(node, responses, endpoint):
            if node['id'] != self.id:
                address = 'http://' + node['ip'] + ':' + node['port']
                response = requests.post(address + endpoint,
                                         data=pickle.dumps(transaction))
                responses.append(response.status_code)

        threads = []
        responses = []
        for node in self.state:
            thread = Thread(target=thread_func, args=(
                node, responses, '/validate_transaction'))
            threads.append(thread)
            thread.start()
        # print("EFTASE EDW - 1")
        for tr in threads:
            tr.join()
        # print("EFTASE EDW - 2")
        # print(responses)
        for res in responses:
            if res != 200:
                return False
        threads = []
        responses = []
        # print("EFTASE EDW - 3")
        for node in self.state:
            thread = Thread(target=thread_func, args=(
                node, responses, '/get_transaction'))
            threads.append(thread)
            thread.start()
        # print("EFTASE EDW - 4")
        # print("EFTASE EDW")
        # if self.current_block.index == 1:
        #     self.broadcast_block(validator)
        #     print("Broadcasted Block")
        #if not flag:
        if self.current_block == None:
            self.current_block = self.create_new_block()
        if not self.add_transaction_to_block(transaction): 
            print("-------new_block--------")
            self.current_block.validator = self.proof_of_stake(self.current_block.previous_hash)
            print("------ Chosen Validator: ", self.current_block.validator, "------")
            self.broadcast_block(self.current_block.validator) 
            print("Broadcasted Block")       
        
        return True

    def broadcast_block(self, validator):

        #self.state = self.calculate_state()
        #self.current_block.state = self.state
        
            
        if self.id == validator:   #the genesis block has no validator   
            # # print("I am running this")
            # self.validated_blocks += 1  # number of times this node has been validator
            # responses = []
            # # broadcasted = False
            # broadcasted = True
            # for node in self.state:
            #     if node["id"]!=self.id:
            #         address = 'http://' + node['ip'] + ':' + node['port']
            #         response = requests.post(address + '/get_block',
            #                              data=pickle.dumps(self.current_block))
            #         responses.append(response)
            # # print(responses) 
            # for res in responses:
            #     # print(res)
                
            #     # if res == 200:
            #     #     broadcasted = True  
            #     if res.status_code != 200:
            #         # print("bad response")
            #         broadcasted = False
            # if broadcasted:
            #     # print("broadcast all good, now to create a new block")
            #     #if node.current_block.previous_hash == node.blockchain.blocks[-1].current_hash
            #     # print("Fees of the Block: ",self.current_block.fees)
            #     self.balance += self.current_block.fees
            #     self.current_block.time_of_death = float(timer())
            #     self.current_block.current_hash = self.current_block.calculate_hash()
            #     self.blockchain.add_block(self.current_block)  
                
            #     self.create_new_block()
            #     # print("Created new Block")

        
            block_accepted = False

            def thread_func(node, responses):
                if node['id'] != self.id:
                    address = 'http://' + node['ip'] + ':' + node['port']
                    response = requests.post(address + '/get_block',
                                             data=pickle.dumps(self.current_block))
                    responses.append(response.status_code)

            threads = []
            responses = []
            for node in self.state:
                thread = Thread(target=thread_func, args=(
                    node, responses))
                threads.append(thread)
                thread.start()

            for tr in threads:
                tr.join()

            for res in responses:
                if res == 200:
                    block_accepted = True

            if block_accepted:
                with self.chain_lock:
                    if self.validate_block(self.current_block):
                        self.balance += self.current_block.fees
                        self.current_block.time_of_death = float(timer())
                        print("-BLOCK ",self.current_block.index, "DIED ", datetime.now())
                        self.current_block.current_hash = self.current_block.calculate_hash()
                        self.blockchain.add_block(self.current_block)  

                        self.create_new_block() 


        #self.state = self.calculate_state()
        #self.current_block.state = self.state
        return True

    def validate_transaction(self, transaction):
        """Validates an incoming transaction.

        The validation consists of:
        - Check that the signature matches
        - Check the the wallet of the sender has enough BCC.
        """
        # print("EFTASE EDW -  79")
        if not transaction.verify_signature():            
            return False
        if self.current_block == None:  
            self.create_new_block()
        # print("EFTASE EDW -  80")   
         
        for node in self.state:

            if node['public_key'] == transaction.sender_address:
                if transaction.type_of_transaction == "first":
                    full_amount = transaction.amount
                elif transaction.type_of_transaction == "coins":                
                    full_amount = 1.03*transaction.amount 
                if transaction.type_of_transaction == "message":
                    full_amount = len(transaction.message)
                if node['balance'] >= full_amount:
                    # if self.current_block != None:
                    #self.current_block.add_transaction(transaction) might be wrong
                    return True
                else:
                    return False
            elif transaction.sender_address == 0:
                return True
        
    
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
        # print("EFTASE EDW")
        if (transaction.sender_address == self.wallet.public_key) or (transaction.receiver_address == self.wallet.public_key):
            # if transaction.type_of_transaction == "message":
            #     fee = len(transaction.message)
            # elif transaction.type_of_transaction == "coins":
            #     fee = 1.03*transaction.amount
            # elif transaction.type_of_transaction == "first":
            #     fee = 0
            # transaction.fee = fee
            # print("EFTASE EDW")
            self.wallet.add_transaction_to_wallet(transaction)
        # if receiver_address == 0
        # Update the balance of the recipient and the sender.
        if self.current_block is None:
            self.current_block = self.create_new_block()
        
        if len(self.current_block.transactions) < self.capacity:
            print("---not full capacity")
            
            fee = 0           
            if transaction.type_of_transaction == 'message':
                fee = len(transaction.message)
                
            if transaction.type_of_transaction == 'coins':                
                fee = transaction.amount*0.03
                    
            for node in self.state: 
                if transaction.receiver_address == 0 and node['public_key'] == transaction.sender_address:
                    node['stake'] = transaction.amount
                    node['balance'] -= transaction.amount


                if node['public_key'] == transaction.sender_address and transaction.type_of_transaction != 'first' and transaction.receiver_address != 0 :
                    node['balance'] -= fee
                    node['balance'] -= transaction.amount

                if node['public_key'] == transaction.receiver_address:
                    node['balance'] += transaction.amount

            self.current_block.add_transaction(transaction)  
            if transaction.type_of_transaction != 'first':
                self.current_block.fees += fee
            
            print("number of transactions in block",len(self.current_block.transactions))
            #print("capacity ", self.capacity)
            return True
        else: 
            print("---full capacity")
            return False

    def proof_of_stake(self, prev_hash):
        random.seed(prev_hash)
        stakes = [node['stake'] for node in self.state]
        print(stakes)
        total_stake = sum(stakes)
        if total_stake == 0:
            # print("MH MPEIS EDW")
            return random.choice(self.state)['id']  # Fallback if no stakes are present

        # summ = 0
        # number = random.randint(0, total_stake)
        # for i, stake in enumerate(stakes):
        #     summ += stake
        #     if number <= summ:
        #         return self.state[i]['id']
                
        stake_thresholds = [stake / total_stake for stake in stakes]
        rng_value = random.random()
        cumulative = 0
        for i, threshold in enumerate(stake_thresholds):
            cumulative += threshold
            if rng_value <= cumulative:
                # print("eftases?")
                return self.state[i]['id']

                
    
        
    def share_blockchain(self, node):
        """Shares the node's current blockchain to a specific node.
        """

        address = 'http://' + node['ip'] + ':' + node['port']
        requests.post(address + '/get_blockchain', data=pickle.dumps(self.blockchain))
        # requests.post(address + '/get_blockchain', data=jsonpickle.encode(self.blockchain))

    def share_state(self, state_node):
        """Shares the node's ring (neighbor nodes) to a specific node.

        This function is called for every newcoming node in the blockchain.
        """

        address = 'http://' + state_node['ip'] + ':' + state_node['port']
        requests.post(address + '/get_state',
                      data=pickle.dumps(self.state))
        
    def parse_file(self):
        #input_file = "C:/Users/odydr/OneDrive/Documents/GitHub/DistributedSystems/5nodes/2nodes.txt" 

        input_file = f"../5nodes_test/trans{self.id}.txt"
        with open(input_file, 'r') as file:
            lines = file.readlines()
        
        # Regular expression pattern to match 'id' followed by a number and the message
        pattern = r'id(\d+)\s+(.*)'
        start_time = float(timer())
        num_of_transactions=0
        for line in lines:
            # Use regular expression to find matches
            match = re.match(pattern, line)
            if match:
                id = int(match.group(1))
                message = match.group(2)
              
            for node in self.state:
                if node['id'] == id:
                    self.create_transaction(node['public_key'], "message", 0, message)
                    num_of_transactions += 1
                    break
        end_time = float(timer())
        print("start_time: ",start_time)
        print("end_time: ",end_time)
        duration = end_time - start_time
        transactions_per_sec = num_of_transactions / duration
        print("Transactions per second : ", transactions_per_sec)
        
        timestamps = []
        for block in self.blockchain.blocks:
            timestamps.append(block.timestamp)        
        
        timestamps.sort()
        print("TIMESTAMPS:",timestamps)
        durations = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
        print("Length of Blockchain: ", len(self.blockchain.blocks))
        avg_block_duration = sum(durations) / len(durations) if durations else 0
        print("Avg block duration : ", avg_block_duration)
        respo = str(transactions_per_sec)+ str(avg_block_duration)

        return (transactions_per_sec, avg_block_duration)

    def validate_block(self, block):
        """Validates an incoming block.

            The validation consists of:
            - check that current hash is valid.
            - validate the previous hash.
        """
        if (self.current_block.validator == self.proof_of_stake(self.current_block.previous_hash) )and (self.current_block.validator == self.proof_of_stake(self.current_block.previous_hash)):#(self.current_block.previous_hash == self.blockchain.blocks[-1].current_hash)
            
            return True
        else:
            
            return False
        
              
       
    def validate_chain(self):
        for block in self.blockchain.blocks[1:]:
            if not self.validate_block(block):
                return False    
        
        return True
