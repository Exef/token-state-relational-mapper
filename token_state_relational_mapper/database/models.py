"""
Database models
"""
from token_state_relational_mapper import db


class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.BigInteger, primary_key=True)
    last_changed_in_block = db.Column(db.BigInteger)
    total_tokens_supply = db.Column(db.Numeric)
    total_tokens_created = db.Column(db.Numeric)
    total_tokens_destroyed = db.Column(db.Numeric)


class TokenHolder(db.Model):
    __tablename__ = 'token_holders'
    id = db.Column(db.BigInteger, primary_key=True)
    last_changed_in_block = db.Column(db.BigInteger)
    address = db.Column(db.Text, nullable=False)
    balance = db.Column(db.Numeric)
    token_turnover = db.Column(db.Numeric)
    held_token_id = db.Column(db.BigInteger, db.ForeignKey('tokens.id'))
    held_token = db.relationship('Token', backref=db.backref('holders', lazy=True))


class BalanceChange(db.Model):
    __tablename__ = 'balance_changes'
    id = db.Column(db.BigInteger, primary_key=True)
    block_time = db.Column(db.BigInteger)
    amount = db.Column(db.Numeric)
    to_address = db.Column(db.Text)
    from_address = db.Column(db.Text)
