import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'tokens.db')
PARITY_NODE_URI = '127.0.0.1:8545'
