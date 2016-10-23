from meta import bot
from utils.chat import crash_message

print('Import helper')


@bot.message_handler(commands=['start'])
def cmd_help(message):
    try:
        raise Exception('Test')
    except:
        crash_message(message)


@bot.message_handler(commands=['start'])
def cmd_start(message):
    pass
