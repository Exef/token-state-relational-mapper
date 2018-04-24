from logging.handlers import RotatingFileHandler

import sys

from logging import captureWarnings
from flask import logging


def init_logger(app):
    app.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    app.logger.addHandler(console_handler)

    # There is a lot of deprecation warnings in current version of web3.
    #  As this code is not meant for production we simply hide them
    captureWarnings(True)

    if 'LOG_FILE_PATH' in app.config:
        file_handler = RotatingFileHandler(app.config['LOG_FILE_PATH'], maxBytes=10000, backupCount=1)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)

    app.logger.debug("Logger initialized.")
