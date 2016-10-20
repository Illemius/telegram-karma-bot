"""
from Illemius/BotCorePlatform/pyBot
"""

import logging
import uuid

from config import DEBUG
from .model import BotLogs

session = str(uuid.uuid4())


def get_logger(name='main'):
    """
    Get logger with stdout and mongo handlers
    :param name: logger name
    :return: logger
    """
    formatter = logging.Formatter(fmt='%(asctime)s[%(name)s][%(levelname)s]: %(message)s',
                                  datefmt="[%d.%m.%Y][%H:%M:%S]"
                                  )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.propagate = False
    if DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    handlers = []
    for handler in logger.handlers:
        handlers.append(handler.__class__)

    if logging.StreamHandler.__class__ not in handlers:
        logger.addHandler(handler)

    if MongoLogger.__class__ not in handlers:
        logger.addHandler(MongoLogger())

    return logger


class MongoLogger(logging.Handler):
    def emit(self, record):

        # Use default formatting:
        self.format(record)

        # Set the database time up:
        if record.exc_info:
            record.exc_text = logging._defaultFormatter.formatException(record.exc_info)
        else:
            record.exc_text = ""
        # Insert log record:
        log = BotLogs()

        log.created = int(record.created)
        log.name = record.name
        log.log_level = record.levelno
        log.log_level_name = record.levelname
        log.message = str(record.msg)
        log.args = str(record.args)
        log.module = record.module
        log.func_name = record.funcName
        log.line_no = record.lineno
        log.exception = record.exc_text
        log.process = record.process
        log.thread = record.thread
        log.thread_name = record.threadName
        log.session = session

        log.save()
