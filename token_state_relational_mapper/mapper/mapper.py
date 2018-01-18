from requests import ReadTimeout
from web3 import Web3, HTTPProvider

from .event_analyzer import TransferEventAnalyzer
from .token_contract_connector import TokenContractConnector
from .state_service import TokenStateService
from .utils import generate_block_ranges


class Mapper:
    def __init__(self, ethereum_node_uri, contract_address, abi_definition, partition_size, max_number_of_retries, logger):
        self.logger = logger
        self.web3 = Web3(HTTPProvider(ethereum_node_uri))
        self.event_analyzer = TransferEventAnalyzer()
        self.contract = TokenContractConnector(self.web3, abi_definition, contract_address, logger)
        self.state_service = TokenStateService(self.contract)
        self.max_number_of_retries = max_number_of_retries
        self.partition_size = partition_size

    def start_mapping(self, starting_block, ending_block, minimum_block_height=0):
        token = self.state_service.get_token_or_create_if_not_exists()

        if starting_block == 'contract_creation':
            starting_block = self.contract.get_initial_block()

        if ending_block == 'latest':
            ending_block = self.web3.eth.blockNumber
            watch_contract = True

        self.logger.info(
            'Started gathering state of token %s from block %s to %s' % (token.name, starting_block, ending_block))
        self._partition_blocks_and_gather_state(token, starting_block, ending_block, self.partition_size)
        self.logger.info(
            'Ended gathering state of token %s from block %s to %s' % (token.name, starting_block, ending_block))

        if watch_contract:
            self.start_watching_latest_blocks(token, ending_block, minimum_block_height)

    def start_watching_latest_blocks(self, token, last_scanned_block, minimum_block_height):
        self.logger.info(
            'Started watching latest blocks for token %s state changes starting from block %i minimal block height is set to %i'
                % (token.name, last_scanned_block, minimum_block_height))
        for new_transfer_events_state in self.contract.watch_contract_state(last_scanned_block, minimum_block_height):
            balance_changes = self.event_analyzer.get_events(new_transfer_events_state)
            self.state_service.add_transfers_to_token(token, balance_changes)

    def _partition_blocks_and_gather_state(self, token, starting_block, ending_block, partition_size, retry_count=1):
        for start, end in generate_block_ranges(starting_block, ending_block, partition_size):
            try:
                self.logger.info('Gather data of token %s from block %s to %s' % (token.name, start, end))
                transfer_events = self.contract.get_state(starting_block, ending_block)
                balance_changes = self.event_analyzer.get_events(transfer_events)
                self.state_service.add_transfers_to_token(token, balance_changes)
            except ReadTimeout as exception:
                self._try_to_retry_mapping(token, start, ending_block, partition_size, retry_count, exception)

    def _try_to_retry_mapping(self, token, new_starting_block, ending_block, partition_size, retry_count, exception):
        if retry_count > self.max_number_of_retries:
            raise exception

        self.logger.warning('Encounter requests.exceptions.ReadTimeout. Retry for %i time' % retry_count)
        self._partition_blocks_and_gather_state(token, new_starting_block, ending_block, partition_size, retry_count + 1)

