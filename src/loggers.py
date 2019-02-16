import os
import logging
from logging.handlers import RotatingFileHandler

import ConfigParser

# root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# conf = ConfigParser.ConfigParser()
# conf.read(root_dir + '/docs/config.ini')
#
DEFAULT_LOGGER_NAME = 'TexasHoldemGame'
DEFAULT_LEVEL = logging.DEBUG
# logger_path = conf.get('log', 'path')
logger_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def get_logger(name=DEFAULT_LOGGER_NAME, level=DEFAULT_LEVEL):
    logger = logging.getLogger(name)
    if len(logger.handlers) == 0:
        logger.setLevel(level)
        path = os.path.join(logger_path, name + '.log')
        # File Handler
        file_handler = RotatingFileHandler(path, maxBytes=1024 * 1024 * 5, backupCount=5)  # limit 5MB
        formatter = logging.Formatter(
            '%(asctime)s [%(name)s][%(filename)s:%(lineno)s][%(funcName)s] <%(levelname)s> %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        # Stream Handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
