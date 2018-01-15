from .models import Token
from .session_provider import get_session


def add_token(token: Token):
    session = get_session()
    session.add(token)
    session.commit()


def get_token(token_address):
    session = get_session()
    token = session.query(Token).filter(Token.address == token_address).first()
    return token