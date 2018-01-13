from flask import Flask

app = Flask('token-state-relational-mapper')
app.config.from_envvar('TSRM_SETTINGS')

from . import routes, models