import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pss

class Transaction:
    """
    Each transaction has:
    - sender_address: the public key of the sender
    - receiver_address: the public key of the recipient
    - type_of_transaction: the type of the transaction, coins or message
    - amount: the amount of the transaction
    - message: the string of the message
    - nonce: the nonce of the transaction
    - transaction_id: the hash of the transaction
    - Signature: the signature of the transaction, proof that the holder of the wallet created the transaction
    """

    def __init__(self, sender_address, receiver_address, type_of_transaction, amount, message, nonce, Signature=None):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.nonce = nonce
        self.transaction_id = self.get_hash()
        self.Signature = None
        self.type_of_transaction = type_of_transaction
        if self.type_of_transaction == 'first':
            self.amount = amount
            self.message = "-"
        elif self.type_of_transaction == 'coins':
            self.amount = amount
            self.message = "-"
        elif self.type_of_transaction == 'message':
            self.message = message
            self.amount = 0
        # self.fee = 0

    def sign_transaction(self, private_key):
        """Sign the current transaction with the given private key."""

        message = self.transaction_id.encode("ISO-8859-1")
        key = RSA.importKey(private_key.encode("ISO-8859-1"))
        h = SHA256.new(message)
        signer = pss.new(key)
        self.Signature = signer.sign(h).decode('ISO-8859-1')

    def get_hash(self):
        """Computes the hash of the transaction."""

        return Crypto.Random.get_random_bytes(128).decode("ISO-8859-1")

    def verify_signature(self):
        """Verifies the signature of a transaction."""

        key = RSA.importKey(self.sender_address.encode('ISO-8859-1'))
        h = SHA256.new(self.transaction_id.encode('ISO-8859-1'))
        verifier = pss.new(key)
        try:
            verifier.verify(h, self.Signature.encode('ISO-8859-1'))
            return True
        except (ValueError, TypeError):
            return False       
        
    def to_list(self):
        """Converts a Transaction object into a list."""
        if self.type_of_transaction == "coins":
            return [self.sender_address, self.receiver_address, self.type_of_transaction, self.amount]
        else:
            return [self.sender_address, self.receiver_address, self.type_of_transaction, self.message]