import time
import datetime

from eth_utils import event_abi_to_log_topic
from web3 import Web3, HTTPProvider
from web3.utils.contracts import find_matching_event_abi
from web3.utils.events import get_event_data


class TokenContractConnector(object):
    def __init__(self, ethereum_node_uri, contract_abi, contract_address, logger):
        self.logger = logger
        self.abi = contract_abi
        self.contract_address = Web3.toChecksumAddress(contract_address)

        self.web3 = Web3(HTTPProvider(ethereum_node_uri))
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.contract_address)

        self.event_abi = find_matching_event_abi(self.abi, event_name="Transfer")
        self.event_topic = event_abi_to_log_topic(self.event_abi)

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

        entries = self.web3.eth.getLogs({
            "address": self.contract_address,
            "fromBlock": start_from_block,
            "toBlock": end_at_block})

        transfers = []
        for raw_event in [entry for entry in entries if entry['topics'][0] == self.event_topic]:
            transfer = get_event_data(self.event_abi, raw_event)
            transfers.append(transfer)

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

    def get_latest_block_number(self):
        return self.web3.eth.blockNumber

    def get_initial_block(self):
        self.logger.debug('Trying to get creation block of contract at address %s' % self.contract_address)
        raise NotImplementedError

    def get_block_dates(self, blocks):
        for block in blocks:
            self.logger.debug('Getting %s block data from node.' % block.number)
            eth_block = self.web3.eth.getBlock(block.number)

            block.date = datetime.datetime.fromtimestamp(eth_block.timestamp)
