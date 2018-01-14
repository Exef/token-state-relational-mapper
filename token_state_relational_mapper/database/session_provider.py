from token_state_relational_mapper import db


def get_session():
    session = db.Session(db.engine)
    return session
