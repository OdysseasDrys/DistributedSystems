class Blockchain:
    """
    The blockchain BlockChat

    it contains blocks (list): list that contains the validated blocks of the chain.
    """

    def __init__(self):
        self.blocks = []

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def add_block(self, block):
        self.blocks.append(block)