"""
Python telegram bot

Illemius/BotCore/Telegram-karma-bot
"""

import logging
import threading

import flask
from TranslateLib import locale_gen, set_locale
from flask import Flask, redirect
from mongoengine import connect

import extensions
import telebot
from config import WEBHOOK_URL, WEB_HOST, WEB_PORT, USE_WEBHOOK, LOGGING_CHAT, DEFAULT_LOCALE, IGNORE_UNREAD_MESSAGES
from meta import MONGO_DATABASE, MONGO_PORT, BOT_URL, WEBHOOK_URL_PATH, bot, LOCALES_PATH
from meta import MONGO_HOST
from models.messages import Messages
from utils.chat_logger import get_chat_logger
from utils.logging import dmesg
from utils.logging import get_dmesg_time
from utils.logging import get_logger

connect(
    db=MONGO_DATABASE,
    host=MONGO_HOST,
    port=MONGO_PORT
)

dmesg('Init app', group='C')
telebot.logger = get_logger('telegram')
telebot.logger.setLevel(logging.DEBUG)

chat_log = get_chat_logger(LOGGING_CHAT, 'core')


def check_ready(update):
    if get_dmesg_time() <= 3:
        telebot.logger.warning('Skip update.')
        return False
    return True


def main():
    locale_gen(LOCALES_PATH)
    set_locale(DEFAULT_LOCALE)

    app = Flask(__name__)

    # Import all chat handlers
    extensions.setup()

    @app.route('/', methods=['GET', 'HEAD'])
    def index():
        """
        Index page
        Always redirect to bot page
        :return:
        """
        return redirect(BOT_URL, code=302)

    # Process webhook calls
    @app.route(WEBHOOK_URL_PATH, methods=['POST'])
    def webhook():
        if flask.request.headers.get('content-type') == 'application/json':
            request = flask.request.get_data().decode("utf-8")
            update = telebot.types.Update.de_json(request)
            if IGNORE_UNREAD_MESSAGES and not check_ready(update):
                return 'sleep'
            if update.message:
                Messages.add(update.message.chat.id, update.message.from_user.id, update.message.content_type)
                bot.process_new_messages([update.message])
            if update.edited_message:
                bot.process_new_edited_messages([update.edited_message])
            if update.inline_query:
                bot.process_new_inline_query([update.inline_query])
            if update.chosen_inline_result:
                bot.process_new_chosen_inline_query([update.chosen_inline_result])
            if update.callback_query:
                bot.process_new_callback_query([update.callback_query])
            return 'ok'
        else:
            flask.abort(403)

    # Setup web server
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    # app.debug = True
    threading.Thread(target=app.run, kwargs={'host': WEB_HOST, 'port': WEB_PORT}).start()

    # Setup webhook
    bot.remove_webhook()
    if USE_WEBHOOK:
        bot.set_webhook(url=WEBHOOK_URL + WEBHOOK_URL_PATH)
    else:
        bot.polling(True)

    chat_log.info('Bot is started. (<code>{:.3f}s</code>)'.format(get_dmesg_time()))


if __name__ == '__main__':
    main()
