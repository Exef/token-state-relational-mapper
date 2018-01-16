from web3 import Web3, HTTPProvider
from .event_analyzer import TransferEventAnalyzer
from .token_contract_connector import TokenContractConnector
from token_state_relational_mapper.mapper.database import Token, TokenHolder, storage_service


class Mapper:
    def __init__(self, ethereum_node_uri, contract_address, abi_definition):
        self.storage_service = storage_service
        self.event_analyzer = TransferEventAnalyzer()
        self.web3 = Web3(HTTPProvider(ethereum_node_uri))
        self.contract_address = contract_address
        self.token_contract = TokenContractConnector(self.web3, abi_definition, self.contract_address)

    def add_token_to_storage_if_not_exists(self):
        existing_token = self.storage_service.get_token(self.contract_address)
        if existing_token is None:
            total_supply, token_name, token_symbol = self.token_contract.get_basic_information()
            self.storage_service.add_token(Token(address=self.contract_address,
                                                 name=token_name,
                                                 symbol=token_symbol,
                                                 total_tokens_supply=total_supply))

    def gather_state_of_token(self, starting_block, ending_block):
        transfer_events = self.token_contract.get_state(starting_block, ending_block)
        balance_changes = self.event_analyzer.get_events(transfer_events)
        self.storage_service.add_balance_changes_to_token(self.contract_address, balance_changes)


