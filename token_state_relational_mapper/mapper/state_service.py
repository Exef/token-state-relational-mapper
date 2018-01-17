from token_state_relational_mapper.mapper.database import Token, TokenHolder, Transfer, Block, get_session


class TokenStateService:
    def __init__(self, token_contract):
        self.token_contract = token_contract
        self.session = get_session()

    def get_token_or_create_if_not_exists(self):
        token = self._get_token(self.token_contract.contract_address)
        if token is None:
            token = self._create_token()
        return token

    def add_transfers_to_token(self, token: Token, transfers: [Transfer]):
        mapped_blocks_numbers = set(map(lambda block: block.number, token.mapped_blocks))
        not_mapped_transfers = filter(lambda t: t.block_time not in mapped_blocks_numbers, transfers)

        block_numbers = set(map(lambda t: t.block_time, transfers))
        self._add_blocks_to_token(token, block_numbers)

        for transfer in not_mapped_transfers:
            self._attach_transfer_to_holders(token, transfer)
            token.transfers.append(transfer)

        self.session.commit()

    def _attach_transfer_to_holders(self, token, transfer):
        from_token_holder = self._get_token_holder_or_create_if_not_exists(token, transfer.from_address)
        to_token_holder = self._get_token_holder_or_create_if_not_exists(token, transfer.to_address)

        transfer.sent_from = from_token_holder
        transfer.sent_to = to_token_holder

        from_token_holder.balance = from_token_holder.balance - transfer.amount

        to_token_holder.balance = to_token_holder.balance + transfer.amount
        to_token_holder.token_turnover = to_token_holder.token_turnover + transfer.amount

        if transfer.is_minting_event():
            token.total_tokens_created = token.total_tokens_created + transfer.amount
        elif transfer.is_burning_transfer():
            token.total_tokens_destroyed = token.total_tokens_destroyed + transfer.amount

        self._update_last_changed_in_block_property(transfer.block_time, from_token_holder, to_token_holder, token)

    def _get_token(self, token_address: str):
        return self.session.query(Token) \
            .filter(Token.address == token_address) \
            .first()

    def _create_token(self):
        token_name, token_symbol, token_total_supply, token_decimals = self.token_contract.get_basic_information()
        token = Token(address=self.token_contract.contract_address,
                      name=token_name,
                      symbol=token_symbol,
                      total_tokens_supply=token_total_supply,
                      decimals=token_decimals)
        self.session.add(token)
        self.session.commit()

        return token

    def _get_token_holder_or_create_if_not_exists(self, token, holder_address):
        token_holder = self._get_token_holder(holder_address, token)

        if token_holder is None:
            token_holder = self._create_new_token_holder(holder_address, token, token_holder)

        return token_holder

    def _get_token_holder(self, holder_address, token):
        token_holder = self.session.query(TokenHolder) \
            .filter(TokenHolder.address == holder_address) \
            .filter(TokenHolder.held_token_id == token.id) \
            .first()

        return token_holder

    def _create_new_token_holder(self, holder_address, token, token_holder):
        token_holder = TokenHolder(address=holder_address, held_token=token)
        self.session.add(token_holder)
        self.session.commit()
        return token_holder

    def _add_blocks_to_token(self, token, block_numbers):
        existing_blocks = self.session.query(Block).filter(Block.number.in_(block_numbers))
        token.mapped_blocks.extend(existing_blocks)

        number_of_existing_blocks = set(map(lambda b: b.number, existing_blocks))
        for block_number in block_numbers:
            if block_number not in number_of_existing_blocks:
                token.mapped_blocks.append(Block(number=block_number))

    @staticmethod
    def _update_last_changed_in_block_property(block_time, *entities):
        for updated_entity in entities:
            if updated_entity.last_changed_in_block is None or updated_entity.last_changed_in_block < block_time:
                updated_entity.last_changed_in_block = block_time
