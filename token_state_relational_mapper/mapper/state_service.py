from token_state_relational_mapper.mapper.database import Token, TokenHolder, Transfer, get_session


class TokenStateService:

    def __init__(self, token_contract):
        self.token_contract = token_contract
        self.session = get_session()

    def add_token(self, token: Token):
        self.session.add(token)
        self.session.commit()

        return token

    def add_transfers_to_token(self, token: Token, transfers: [Transfer]):
        for transfer in transfers:
            self.attach_transfer_to_holders(token, transfer)

        token.transfers.extend(transfers)
        self.session.commit()

    def attach_transfer_to_holders(self, token, transfer):
        from_token_holder = self.get_token_holder_or_create_if_not_exists(token, transfer.from_address)
        to_token_holder = self.get_token_holder_or_create_if_not_exists(token, transfer.to_address)

        transfer.sent_from = from_token_holder
        transfer.sent_to = to_token_holder

        from_token_holder.balance = from_token_holder.balance - transfer.amount

        to_token_holder.balance = to_token_holder.balance + transfer.amount
        to_token_holder.token_turnover = to_token_holder.token_turnover + transfer.amount

        if transfer.is_minting_event():
            token.total_tokens_created = token.total_tokens_created + transfer.amount
        elif transfer.is_burning_transfer():
            token.total_tokens_destroyed = token.total_tokens_destroyed + transfer.amount

        self.update_last_changed_in_block_property(transfer.block_time, from_token_holder, to_token_holder, token)

    def get_token_or_create_if_not_exists(self):
        token = self.get_token(self.token_contract.contract_address)
        if token is None:
            token = self.create_token()
        return token

    def get_token(self, token_address: str):
        return self.session.query(Token) \
            .filter(Token.address == token_address) \
            .first()

    def create_token(self):
        total_supply, token_name, token_symbol = self.token_contract.get_basic_information()
        token = self.add_token(Token(address=self.token_contract.contract_address,
                                     name=token_name,
                                     symbol=token_symbol,
                                     total_tokens_supply=total_supply))

        return token

    def get_token_holder_or_create_if_not_exists(self, token, holder_address):
        token_holder = self.get_token_holder(holder_address, token)

        if token_holder is None:
            token_holder = self.create_new_token_holder(holder_address, token, token_holder)

        return token_holder

    def get_token_holder(self, holder_address, token):
        token_holder = self.session.query(TokenHolder) \
            .filter(TokenHolder.address == holder_address) \
            .filter(TokenHolder.held_token_id == token.id) \
            .first()

        return token_holder

    def create_new_token_holder(self, holder_address, token, token_holder):
        token_holder = TokenHolder(address=holder_address, held_token=token)
        self.session.add(token_holder)
        self.session.commit()
        return token_holder

    @staticmethod
    def update_last_changed_in_block_property(block_time, *entities):
        for updated_entity in entities:
            if updated_entity.last_changed_in_block is None or updated_entity.last_changed_in_block < block_time:
                updated_entity.last_changed_in_block = block_time
