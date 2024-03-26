



class Transaction:
    """
    Each transaction has:
    - sender_adress: the public key of the sender
    - receiver_adress: the public key of the recipient
    - type_of_transaction: the type of the transaction, coins or message
    - amount: the amount of the transaction
    - message: the string of the message
    - nonce: the nonce of the transaction
    - transaction_id: the hash of the transaction
    - Signature: the signature of the transaction, proof that the holder of the wallet created the transaction
    """

    def __init__(self, sender_adress, receiver_adress, type_of_transaction, amount, message, nonce, transaction_id, Signature):
        self.sender_adress = sender_adress
        self.receiver_adress = receiver_adress
        self.nonce = nonce
        self.transaction_id = transaction_id
        self.Signature = Signature
        self.type_of_transaction = type_of_transaction
        if self.type_of_transaction == 'coins':
            self.amount = amount
            self.message = None
        elif self.type_of_transaction == 'message':
            self.message = message
            self.amount = None

        

        

        