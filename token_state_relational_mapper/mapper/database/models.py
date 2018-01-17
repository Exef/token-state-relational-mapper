"""
Database models
"""
from token_state_relational_mapper import db

zero_address = '0x0000000000000000000000000000000000000000'


class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.Text, unique=True)
    last_changed_in_block = db.Column(db.Integer)
    name = db.Column(db.Text)
    symbol = db.Column(db.Text)
    decimals = db.Column(db.Numeric(scale=0), default=0)
    total_tokens_supply = db.Column(db.Numeric(scale=0), default=0)
    total_tokens_created = db.Column(db.Numeric(scale=0), default=0)
    total_tokens_destroyed = db.Column(db.Numeric(scale=0), default=0)

    transfers = db.relationship("Transfer")
    token_holders = db.relationship("TokenHolder", back_populates='held_token')


class TokenHolder(db.Model):
    __tablename__ = 'token_holders'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.Text, nullable=False)

    last_changed_in_block = db.Column(db.Integer)
    balance = db.Column(db.Numeric(scale=0), default=0)
    token_turnover = db.Column(db.Numeric(scale=0), default=0)

    held_token_id = db.Column(db.Integer, db.ForeignKey('tokens.id'))
    held_token = db.relationship('Token')


class Transfer(db.Model):
    __tablename__ = 'transfers'
    id = db.Column(db.Integer, primary_key=True)

    block_time = db.Column(db.Integer)
    amount = db.Column(db.Numeric(scale=0))

    token_id = db.Column(db.Integer, db.ForeignKey('tokens.id'))
    token = db.relationship('Token', back_populates='transfers')

    to_address = db.Column(db.Text)
    from_address = db.Column(db.Text)

    sent_from_id = db.Column("sent_from_id", db.Integer, db.ForeignKey("token_holders.id"))
    sent_from = db.relationship("TokenHolder", backref="sent_transfers", foreign_keys='Transfer.sent_from_id')

    sent_to_id = db.Column("sent_to_id", db.BigInteger, db.ForeignKey("token_holders.id"))
    sent_to = db.relationship("TokenHolder", backref="received_transfers", foreign_keys='Transfer.sent_to_id')

    def is_minting_event(self):
        return self.from_address == zero_address

    def is_burning_transfer(self):
        return self.to_address == zero_address
