import logging

import sys

from config import LOGGING_TO_CHAT
from meta import bot
from .logging import get_logger


def get_chat_logger(chat_id, name='telebug'):
    logger = get_logger(name)
    formatter = logging.Formatter(fmt='#%(name)s #%(levelname)s: %(message)s')
    handler = TelegramLogger(chat_id)
    handler.setFormatter(formatter)

    for log_handler in logger.handlers:
        if type(log_handler) is TelegramLogger:
            if handler.chat_id == chat_id:
                continue
        logger.addHandler(handler)
        break

    return logger


class TelegramLogger(logging.Handler):
    def __init__(self, chat_id, *args, **kwargs):
        super(TelegramLogger, self).__init__(*args, **kwargs)
        self.chat_id = chat_id

    def emit(self, record):
        try:
            if LOGGING_TO_CHAT:
                bot.send_message(self.chat_id, self.format(record), parse_mode='html', disable_web_page_preview=True)
        except:
            print(sys.exc_info())
