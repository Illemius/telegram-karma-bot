import sys
import time

from TranslateLib import translate as _

import telebot
from config import LOGGING_CHAT
from meta import bot, root_user
from models.dialogs import Dialogs
from utils.chat_logger import get_chat_logger
from utils.logging import CrashReport

chat_log = get_chat_logger(LOGGING_CHAT, 'main')


def typing(message, timeout=.5):
    if timeout > .0:
        time.sleep(timeout)
    if type(message) is int:
        chat_id = message
    else:
        chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')


def get_username_or_name(user):
    if type(user) not in [telebot.types.User, telebot.types.Chat]:
        return '<USER>'
    if user.username is None:
        name = '{} {}'.format(user.first_name or '', user.last_name or '').strip()
        return name if len(name) else user.id
    return '@' + user.username


def cant_send_private(message, locale=None):
    bot.reply_to(message, _('can not sent private message', locale=locale))


def crash_message(message):
    c = CrashReport(*sys.exc_info())
    try:
        c.save()
        telebot.logger.error('\n\t'.join(c.formatted_traceback))
        bot.send_message(message.chat.id, 'Во время выполнения команды произошла ошибка :с\n'
                                          'Если не сложно, перешли, пожалуйста это сообщение разработчику '
                                          '{user}\n'
                                          'Report: {id}-{file}'.format(user=get_username_or_name(root_user),
                                                                       id=c.id, file=c.filename))
        chat_log.error('Crash report: <b>{id}</b>\n'
                       'File: <b>{file}</b>\n'
                       'User: {login} ({uid})\n'
                       '<pre>{traceback}</pre>'.format(id=c.id, file=c.filename,
                                                       login=get_username_or_name(message.from_user),
                                                       uid=message.from_user.id,
                                                       traceback='\n'.join(c.formatted_traceback)))
    except:
        cc = CrashReport(*sys.exc_info())
        print('\n'.join(c.formatted_traceback), file=sys.stderr)
        print('\n'.join(cc.formatted_traceback), file=sys.stderr)


def get_dialog_object(index):
    dialogs = Dialogs.objects(index=index)
    if len(dialogs):
        return dialogs[0]
    else:
        return Dialogs(index=index)


class ParseUserData(object):
    def __init__(self, function):
        self.function = function

    def __call__(self, message):
        return self.function(message,
                             user=get_dialog_object(message.from_user.id),
                             chat=get_dialog_object(message.chat.id))


KEY_SPLITTER = '^~'
DATA_SPLITTER = "^^:"


def generate_inline_data(key: str, data: list):
    return '{}{}{}'.format(key, KEY_SPLITTER, DATA_SPLITTER.join(data))


def parse_inline_data(data):
    key = data.split(KEY_SPLITTER)[0]
    data = data[len(key) + len(KEY_SPLITTER):].split(DATA_SPLITTER)
    return key, data
