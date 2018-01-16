from .models import Token, TokenHolder, Transfer
from .session_provider import get_session


def add_token(token: Token):
    session = get_session()
    session.add(token)
    session.commit()


def get_token(token_address: str, session=None):
    if session is None:
        session = get_session()
    token = session.query(Token).filter(Token.address == token_address).first()
    return token


def get_token_holder(session, token, holder_address):
    token_holder = session.query(TokenHolder) \
        .filter(TokenHolder.address == holder_address) \
        .filter(TokenHolder.held_token_id == token.id) \
        .first()

    if token_holder is None:
        token_holder = TokenHolder(address=holder_address, held_token=token)
        session.add(token_holder)
        session.commit()

    return token_holder


def attach_transfer_to_holders(token, transfer, session):
    from_token_holder = get_token_holder(session, token, transfer.from_address)
    to_token_holder = get_token_holder(session, token, transfer.to_address)

    transfer.sent_from = from_token_holder
    transfer.sent_to = to_token_holder

    from_token_holder.balance = from_token_holder.balance - transfer.amount
    from_token_holder.last_changed_in_block = transfer.block_time

    to_token_holder.balance = to_token_holder.balance + transfer.amount
    to_token_holder.token_turnover = to_token_holder.token_turnover + transfer.amount
    to_token_holder.last_changed_in_block = transfer.block_time


def add_transfers_to_token(token_address: str, transfers: [Transfer]):
    session = get_session()
    token = get_token(token_address, session)

    for transfer in transfers:
        attach_transfer_to_holders(token, transfer, session)

    token.transfers.extend(transfers)

    session.commit()
