from blockchain import Blockchain
from block import Block
from wallet import Wallet
from transaction import Transaction
import requests
import pickle

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
        self.bcc = 0
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
                amount = len(message)
                fee = 0.03*amount
                if (self.balance >= (amount+fee)):
                    transaction = Transaction(self.wallet.public_key, receiver_adress, type_of_transaction, None, message, self.wallet.nonce)
                    self.block.fees += fee
                    self.balance -= fee+amount
                
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
        if self.bcc() >= amount:
            stake_transaction = Transaction(self.wallet.public_key, 0, 'coins', amount, None,)
            self.stake_amount = amount
            return True
        else:
            print("Not enough BCC")
            return False

    def broadcast_transaction(self, transaction):

        for node in self.state:
            try:
                r = requests.post(f'{h}/{api}/', message, **kwargs)

            # cant do too much
                if r.status_code != 200:
                    print(f'broadcast: Request "{h}/{api}" failed')

            except requests.exceptions.Timeout:
                print(f'broadcast: Request "{h}/{api}" timed out')
                pass



