from logging.handlers import RotatingFileHandler

import sys

from flask import logging


def init_logger(app):
    app.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    app.logger.addHandler(console_handler)
    if 'LOG_FILE_PATH' in app.config:
        file_handler = RotatingFileHandler(app.config['LOG_FILE_PATH'], maxBytes=10000, backupCount=1)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)

    app.logger.debug("Logger initialized.")
