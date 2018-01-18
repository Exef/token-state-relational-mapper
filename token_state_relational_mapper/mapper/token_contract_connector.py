import time


class TokenContractConnector:
    def __init__(self, web3_instance, contract_abi, contract_address, logger):
        self.logger = logger
        self.event_name = 'Transfer'
        self.abi = contract_abi
        self.contract_address = contract_address
        self.web3 = web3_instance
        self.contract = self.web3.eth.contract(self.abi, contract_address)

    def get_basic_information(self):
        self.logger.debug('Getting basic token information from contract at address %s' % self.contract_address)
        token_name = self.contract.call().name()
        total_supply = self.contract.call().totalSupply()
        token_symbol = self.contract.call().symbol()
        token_decimal_places = self.contract.call().decimals()

        return token_name, token_symbol, total_supply, token_decimal_places

    def get_state(self, start_from_block, end_at_block):
        self.logger.debug(
            'Getting state of token from contract at address %s from block %s to %s' % (
                self.contract_address, start_from_block, end_at_block))

        filters = {'fromBlock': start_from_block, 'toBlock': end_at_block}
        transfers_filter = self.contract.on(self.event_name, filters)

        transfers = transfers_filter.get(only_changes=False)
        self.logger.debug(
            'Found %i transfers of token from contract at address %s from block %s to %s'
            % (len(transfers), self.contract_address, start_from_block, end_at_block))

        return transfers

    def watch_contract_state(self, last_scanned_block, minimum_block_height):
        while True:
            current_block = self.web3.eth.blockNumber
            self.logger.debug('Current block: %s Last_scanned_block: %s' % (current_block, last_scanned_block))
            if last_scanned_block + minimum_block_height < current_block:
                yield self.get_state(last_scanned_block, current_block - minimum_block_height)
                last_scanned_block = current_block - minimum_block_height

            time.sleep(60)

    def get_initial_block(self):
        self.logger.debug('Trying to get creation block of contract at address %s' % self.contract_address)
        raise NotImplementedError
