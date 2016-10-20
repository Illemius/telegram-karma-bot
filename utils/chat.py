import sys

import telebot
from config import LOGGING_CHAT
from meta import bot, root_user
from utils.chat_logger import get_chat_logger
from utils.logging import CrashReport

chat_log = get_chat_logger(LOGGING_CHAT, 'main')


def typing(message):
    bot.send_chat_action(message.chat.id, 'typing')


def get_username_or_name(user):
    if user.username is None:
        name = '{} {}'.format(user.first_name or '', user.last_name or '').strip()
        return name if len(name) else user.id
    return '@' + user.username


def crash_message(message):
    c = CrashReport(*sys.exc_info())
    try:
        c.save()
        telebot.logger.error('\n\t'.join(c.formatted_traceback))
        bot.send_message(message.chat.id, 'Во время выполнения команды произошла ошибка :с\n'
                                          'Если не сложно, перешли, пожалуйста это сообщение разработчику '
                                          '{user}n'
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
