import logging
import os
import sys

from pytz import timezone

import telebot
from config import WEBHOOK_URL, TOKEN, TIMEZONE as TZ_NAME, ROOT_UID

BUILD = 'b0001'

# Setup bot location
TIMEZONE = timezone(TZ_NAME)

# Base application dir
# Usage: os.path.join(<BASE_DIR or APP_DIR>, '<file.name>')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

# === Telegram ===

WEBHOOK_URL_BASE = "https://%s" % WEBHOOK_URL
WEBHOOK_URL_PATH = "/%s" % 'webhook'

bot = telebot.TeleBot(TOKEN)
root_user = bot.get_chat(ROOT_UID)

BOT_URL = 'https://telegram.me/'.format(bot.get_me().username)

# === Logging ===
LOG_LEVEL = logging.DEBUG
CRASHREPORT_LOCATION = os.path.join(APP_DIR, 'crash')
REPORTS_LOCATION = os.path.join(APP_DIR, 'dumps')

# === MongoDB & MongoEngine ===
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DATABASE = 'telekarma'
