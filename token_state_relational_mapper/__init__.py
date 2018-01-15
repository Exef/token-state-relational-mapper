"""
Simple ERC20 token state relational mapper service that gathers data from Ethereum blockchain about specific token.
Recent token state is stored in the database.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask('token_state_relational_mapper')
app.config.from_envvar('TSRM_SETTINGS')

db = SQLAlchemy(app)

from . import routes
from token_state_relational_mapper.mapper.database import models
