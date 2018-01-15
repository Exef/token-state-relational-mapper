class TokenContractConnector:
    def __init__(self, web3_instance, contract_abi, contract_address):
        self.abi = contract_abi
        self.contract_address = contract_address
        self.web3 = web3_instance
        self.contract = self.web3.eth.contract(self.abi, contract_address)

    def get_basic_information(self):
        token_name = self.contract.call().name()
        total_supply = self.contract.call().totalSupply()
        token_symbol = self.contract.call().symbol()
        token_decimal_places = self.contract.call().decimals()
        real_total_supply = total_supply / (10 ** token_decimal_places)

        return real_total_supply, token_name, token_symbol

    def get_state(self, starting_block, ending_block):
        start_from_block = starting_block
        end_at_block = ending_block
        if end_at_block is None:
            end_at_block = 'latest'

        filters = {'fromBlock': start_from_block, 'toBlock': end_at_block}

        transfers_filter = self.contract.on('Transfer', filters)
        return transfers_filter.get(only_changes=False)
