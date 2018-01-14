import json
from os import path
from web3 import Web3, HTTPProvider
from .mapper_options import MapperOptions
from token_state_relational_mapper.database import Token, session_provider


class Mapper:
    def __init__(self, ethereum_node_uri, options: MapperOptions):
        self.web3 = Web3(HTTPProvider(ethereum_node_uri))

        with open(str(path.join(path.abspath(path.dirname(__file__)), 'erc20_abi.json')), 'r') as abi_definition:
            self._abi = json.load(abi_definition)

        self.contract = self.web3.eth.contract(self._abi, options.contract_address)
        self.session = session_provider.get_session()
        self.options = options

    def add_token_to_storage_if_not_exists(self):
        existing_token = self.session.query(Token).filter(Token.address == self.options.contract_address).first()

        if existing_token is None:
            total_supply, token_name, token_symbol = self._get_token_information_from_contract()

            self.session.add(Token(address=self.options.contract_address,
                                   name=token_name,
                                   symbol=token_symbol,
                                   total_tokens_supply=total_supply))
            self.session.commit()

    def _get_token_information_from_contract(self):
        token_name = self.contract.call().name()
        total_supply = self.contract.call().totalSupply()
        token_symbol = self.contract.call().symbol()
        token_decimal_places = self.contract.call().decimals()

        real_total_supply = total_supply / (10 ** token_decimal_places)

        return real_total_supply, token_name, token_symbol
