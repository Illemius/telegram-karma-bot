import json

from meta import bot
from utils.cache import users_cache
from utils.chat import crash_message
from utils.karma import generate_karma_cache, karma_transaction

generate_karma_cache()


@bot.message_handler(commands=['test'])
def cmd_test(message):
    try:
        bot.send_message(message.chat.id, 'ok')
        karma_transaction(message.chat, 0, message.from_user, 10, 'test transaction')
        # bot.send_message(message.chat.id, json.dumps(users_cache, indent=4, separators=[', ', ': ']))
    except:
        crash_message(message)
