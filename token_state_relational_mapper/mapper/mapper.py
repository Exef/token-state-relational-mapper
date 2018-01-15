from web3 import Web3, HTTPProvider

from .token_contract_connector import TokenContractConnector
from .mapper_options import MapperOptions
from token_state_relational_mapper.database import Token, session_provider


class Mapper:
    def __init__(self, ethereum_node_uri, options: MapperOptions, abi_definition):
        self.session = session_provider.get_session()
        self.options = options
        self.web3 = Web3(HTTPProvider(ethereum_node_uri))
        self.token_contract = TokenContractConnector(self.web3, abi_definition, options.contract_address)

    def add_token_to_storage_if_not_exists(self):
        existing_token = self.session.query(Token).filter(Token.address == self.options.contract_address).first()

        if existing_token is None:
            total_supply, token_name, token_symbol = self.token_contract.get_basic_information()

            self.session.add(Token(address=self.options.contract_address,
                                   name=token_name,
                                   symbol=token_symbol,
                                   total_tokens_supply=total_supply))
            self.session.commit()

    def gather_state_of_token(self):
        transfer_events = self.token_contract.get_state(self.options.starting_block, self.options.ending_block)
        print(transfer_events)
