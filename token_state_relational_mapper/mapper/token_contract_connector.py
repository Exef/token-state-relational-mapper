class TokenContractConnector:
    def __init__(self, web3_instance, contract_abi, contract_address):
        self.event_name = 'Transfer'
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

    def get_state(self, start_from_block, end_at_block):
        filters = {'fromBlock': start_from_block, 'toBlock': end_at_block}
        transfers_filter = self.contract.on(self.event_name, filters)

        return transfers_filter.get(only_changes=False)
