class Blockchain:
    """
    The blockchain BlockChat

    it contains blocks (list): list that contains the validated blocks of the chain.
    """

    def __init__(self):
        """Initiliazes the blockchain"""
        self.blocks = []

    def __str__(self):
        """Returns a string representation of the blockchain"""
        return str(self.__class__) + ": " + str(self.__dict__)

    def add_block(self, block):
        """Adds a block to the blockchain"""
        self.blocks.append(block)