from web3 import Web3, HTTPProvider

from .event_analyzer import TransferEventAnalyzer
from .token_contract_connector import TokenContractConnector
from .state_service import TokenStateService


class Mapper:
    def __init__(self, ethereum_node_uri, contract_address, abi_definition, logger):
        self.logger = logger
        self.web3 = Web3(HTTPProvider(ethereum_node_uri))
        self.event_analyzer = TransferEventAnalyzer()
        self.contract = TokenContractConnector(self.web3, abi_definition, contract_address)
        self.service = TokenStateService(self.contract)

    def start_mapping(self, starting_block, ending_block):
        token = self.service.get_token_or_create_if_not_exists()
        self.logger.info(
            'Started gathering state of token %s from block %i to %i' % (token.name, starting_block, ending_block))

        self.gather_state_of_token(token, starting_block, ending_block)

        self.logger.info(
            'Ended gathering state of token %s from block %i to %i' % (token.name, starting_block, ending_block)
        )

    def gather_state_of_token(self, token, starting_block, ending_block):
        transfer_events = self.contract.get_state(starting_block, ending_block)
        balance_changes = self.event_analyzer.get_events(transfer_events)
        self.service.add_transfers_to_token(token, balance_changes)
