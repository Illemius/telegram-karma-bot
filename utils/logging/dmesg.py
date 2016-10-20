"""
from Illemius/BotCorePlatform/pyBot
"""

import time

from . import get_logger

_messages = []
_first_message = None

log = get_logger('DMESG')


class DebugMessage:
    def __init__(self, group, message):
        self.time = time.time()
        self.group = group
        self.message = message

        global _first_message
        if not _first_message:
            _first_message = self.time

    def __str__(self):
        return '[{:.3f}] {}: {}'.format(self.time - _first_message, self.group.upper(), self.message)

    def __repr__(self):
        return '<DMESG "{}">'.format(self.__str__())


def dmesg(*args, group='', split=''):
    # Regen text
    text = []
    for item in args:
        text.append(str(item))

    # Memorize message
    message = DebugMessage(group, split.join(text))
    _messages.append(message)

    # Out message
    log.debug(message)


def get_dmesg_time():
    return time.time() - _first_message


def get_dmesg(as_str_list=False, as_text=False):
    if as_text:
        return '\n'.join(get_dmesg(as_str_list))
    if as_str_list:
        return [str(message) for message in _messages]
    return _messages
