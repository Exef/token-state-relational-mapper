from .event_analyzer import TransferEventAnalyzer
from .state_service import TokenStateService
from .token_contract_connector import TokenContractConnector
from .utils import generate_block_ranges


class Mapper:
    def __init__(self, ethereum_node_uri, contract_address, abi_definition, partition_size, max_number_of_retries, logger):
        self.logger = logger
        self.max_number_of_retries = max_number_of_retries
        self.partition_size = partition_size
        self.watch_contract = False

        self.event_analyzer = TransferEventAnalyzer()
        self.contract = TokenContractConnector(ethereum_node_uri, abi_definition, contract_address, logger)
        self.state_service = TokenStateService(self.contract)

    def start_mapping(self, starting_block, ending_block, minimum_block_height=0):
        token = self.state_service.get_token_or_create_if_not_exists()

        if starting_block == 'contract_creation':
            starting_block = self.contract.get_initial_block()

        if ending_block == 'latest':
            ending_block = self.contract.get_latest_block_number()
            self.watch_contract = True

        self.logger.info(
            'Started gathering state of token %s from block %s to %s' % (token.name, starting_block, ending_block))
        self._partition_blocks_and_gather_state(token, starting_block, ending_block, self.partition_size)
        self.logger.info(
            'Ended gathering state of token %s from block %s to %s' % (token.name, starting_block, ending_block))

        if self.watch_contract:
            self.start_watching_latest_blocks(token, ending_block, minimum_block_height)

    def start_watching_latest_blocks(self, token, last_scanned_block, minimum_block_height):
        self.logger.info(
            'Started watching latest blocks for token %s state changes starting from block %i minimal block height is set to %i'
                % (token.name, last_scanned_block, minimum_block_height))
        for new_transfer_events_state in self.contract.watch_contract_state(last_scanned_block, minimum_block_height):
            balance_changes = self.event_analyzer.get_events(new_transfer_events_state)
            self.state_service.add_transfers_to_token(token, balance_changes)
            self._add_date_to_blocks()

    def _partition_blocks_and_gather_state(self, token, starting_block, ending_block, partition_size, retry_count=1):
        for start, end in generate_block_ranges(starting_block, ending_block, partition_size):
            try:
                self.logger.info('Gather data of token %s from block %s to %s' % (token.name, start, end))
                transfer_events = self.contract.get_state(start, end)
                self._map_incoming_transfer_events(token, transfer_events)
                self._add_date_to_blocks()
            except Exception as exception:
                self._try_to_retry_mapping(token, start, ending_block, partition_size, retry_count, exception)

    def _map_incoming_transfer_events(self, token, transfer_events):
        balance_changes = self.event_analyzer.get_events(transfer_events)
        self.state_service.add_transfers_to_token(token, balance_changes)

    def _try_to_retry_mapping(self, token, new_starting_block, ending_block, partition_size, retry_count, exception):
        if retry_count > self.max_number_of_retries:
            raise exception

        self.logger.warning('Retry for %i time' % retry_count)
        self._partition_blocks_and_gather_state(token, new_starting_block, ending_block, partition_size, retry_count + 1)

    def _add_date_to_blocks(self):
        blocks_no_date = self.state_service.get_blocks_without_date()
        self.contract.get_block_dates(blocks_no_date)

