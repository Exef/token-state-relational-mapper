from .models import Token, Transfer
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


def add_balance_changes_to_token(token_address: str, balance_changes: [Transfer]):
    session = get_session()
    token = get_token(token_address, session)
    token.transfers.extend(balance_changes)
    session.commit()
