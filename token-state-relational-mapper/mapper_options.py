class MapperOptions:
    """
    Class for storing ERC20 token state mapper
    """
    def __init__(self, contract_address, starting_block, ending_block, minimum_block_height):
        self.contract_address = contract_address
        self.starting_block = starting_block
        self.ending_block = ending_block
        self.minimum_block_height = minimum_block_height

    def serialize(self):
        return {
            'contract_address': self.contract_address,
            'starting_block': self.starting_block,
            'ending_block': self.ending_block,
            'minimum_block_height': self.minimum_block_height
        }
