import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask('token_state_relational_mapper')
app.config.from_envvar('TSRM_SETTINGS')

db = SQLAlchemy(app)

from . import routes, models