from blockchain import Blockchain
from block import Block
from wallet import Wallet
from transaction import Transaction
import requests
import pickle
import random

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
        state (list): list of information about other nodes
                     (id, ip, port, public_key, balance, stake_amount).
        stake_amount (int): the amount of BCC that the node has staked.        
        
    """

    def __init__(self):
        """Initializes a Node."""
        self.id = None
        self.balance = 0
        self.generate_wallet()
        self.blockchain = Blockchain()
        self.current_block = None
        self.capacity = None
        self.state = []
        self.stake_amount = 0
        
    def __str__(self): 
        return str(self.__class__) + ": " + str(self.__dict__)
    
    def add_transaction(self, transaction):
        """Add a transaction to the node's wallet."""
        self.wallet.add_transaction(transaction)

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

    def create_transaction(self, receiver_adress, type_of_transaction, amount, message):
        """Create a transaction for the node."""
        if receiver_adress != 0:
            if type_of_transaction == 'coins':
                fee = 0.03*amount
                if (self.balance >= (amount+fee)):
                    self.wallet.nonce += 1
                    transaction = Transaction(self.wallet.public_key, receiver_adress, type_of_transaction, amount, None, self.wallet.nonce)
                    self.block.fees += fee
                    self.balance -= fee+amount
            if type_of_transaction == 'message':
                fee = len(message)
                if (self.balance >= fee):
                    transaction = Transaction(self.wallet.public_key, receiver_adress, type_of_transaction, None, message, self.wallet.nonce)
                    self.block.fees += fee
                    self.balance -= fee
                    self.wallet.nonce += 1
                
        else: #in case it is a stake transaction 
            if amount >= self.balance:
                 self.wallet.nonce += 1
                 transaction = Transaction(self.wallet.public_key, receiver_adress, type_of_transaction, amount, None, self.wallet.nonce)
                 self.balance -= amount
                 # also send stake to endpoint 

        transaction.sign_transaction(self.wallet.private_key)

        if self.broadcast_transaction(transaction):
            return True
        else:
            return False         



    def get_transaction(self , transaction = None): 
        """Get a transaction from the node's wallet."""
        return self.wallet.get_transaction(transaction)
    
    def stake(self, amount):
        """Set the node's stake."""
        if self.balance() >= amount:
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
        for node in self.state:
            try:
                address = 'http://' + node['ip'] + ':' + node['port']
                response = requests.post(address + '/validate_transaction',
                                         data=pickle.dumps(transaction))
                # if response.status_code != 200:
                #     print(f'broadcast: Request "{node['ip']}/{node['port']}" failed')
                

            except requests.exceptions.Timeout:
                # print(f'broadcast: Request "{node['ip']}/{node['port']}" timed out')
                pass

        self.add_transaction_to_block(transaction)
        
        return True

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
                if transaction.type_of_message == "coins":                
                    full_amount = 1.03*transaction.amount 
                if transaction.type_of_message == "message":
                    full_amount = len(transaction.message)
                if node['balance'] >= full_amount:
                    return True
        return False


    def add_transaction_to_block(self, transaction):
        
        #if node sender or receiver add transaction 
        if (transaction.sender_adress == self.wallet.public_key) or (transaction.receiver_adress == self.wallet.public_key):
             self.wallet.add_transaction(transaction)

        # Update the balance of the recipient and the sender.
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

        if not self.current_block.add_transaction(transaction):
            random.seed(self.current_block.previous_hash)
            stakes = [node['stake'] for node in self.state]
            total_stake = sum(stakes)
            if total_stake == 0:
                return random.choice(self.state)['id']  # Fallback if no stakes are present

            # stake_thresholds = [stake / total_stake for stake in stakes]
            # rng_value = random.random()
            # cumulative = 0
            # for i, threshold in enumerate(stake_thresholds):
            #     cumulative += threshold
            #     if rng_value <= cumulative:
            #         return self.state[i]['id']
            sum = 0
            number = random.randint(0,total_stake)
            for i in enumerate(stakes):
                sum += stakes[i]
                if number <= sum:
                    return self.state[i]['id']