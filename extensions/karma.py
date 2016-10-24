import re

from TranslateLib import bool_to_str

from meta import bot
from utils import karma_votes_calculator
from utils.chat import crash_message, ParseUserData, get_username_or_name, typing
from utils.karma import generate_karma_cache, karma_transaction, get_cached_user_karma

generate_karma_cache()
KARMA_CHANGE_REGEX = '^(?P<vote>[+\-]{2,})(?P<description>.+)?'


def vote_message(message, user, description, amount=1):
    # TODO: anti spam
    if bool(message.reply_to_message) and message.reply_to_message.from_user.id != message.from_user.id:
        karma_transaction(message.chat, message.from_user, message.reply_to_message.from_user,
                          amount=amount,
                          description=bool_to_str(amount > 0, 'good message', 'bad message'),
                          transfer=False)

        if user.subscribe or True:
            try:
                # TODO: translate
                if amount > 0:
                    text = '{user} поблагодарил Вас в чате {chat}'
                elif amount < 0:
                    text = '{user} не понравилось Ваше сообщение в чате {chat}'
                else:
                    text = 'Пользователь {} безразличен к вашему сообщению в чате {}'

                if len(description):
                    text += '\n' + 'Комментарий: {text}'
                bot.send_message(message.reply_to_message.from_user.id, text.format(
                    user=get_username_or_name(message.from_user),
                    chat=message.reply_to_message.chat.title,
                    text=description
                ), disable_web_page_preview=True)
                bot.forward_message(message.reply_to_message.from_user.id,
                                    message.chat.id, message.reply_to_message.message_id,
                                    disable_notification=True)
            except:
                pass


def exec_vote_cmd(message, user, amount):
    try:
        description_pos = 0
        for messageEntity in message.entities:
            if messageEntity.type == 'bot_command':
                description_pos = messageEntity.offset + messageEntity.length
                break
        description = message.text[description_pos:]
        vote_message(message, user, description, amount)
    except:
        return crash_message(message)


@bot.message_handler(commands=['good', 'tnx', 'thanks'])
@ParseUserData
def cmd_tnx(message, user, chat):
    typing(message)
    exec_vote_cmd(message, user, 1)


@bot.message_handler(commands=['bad'])
@ParseUserData
def cmd_bad(message, user, chat):
    typing(message)
    exec_vote_cmd(message, user, -1)


@bot.message_handler(regexp=KARMA_CHANGE_REGEX)
@ParseUserData
def cmd_vote_symbols(message, user, chat):
    try:
        amount, description = karma_votes_calculator.parse_message(message.text)
        vote_message(message, user, description, amount)
    except:
        crash_message(message)


@bot.message_handler(commands=['test'])
def cmd_test(message):
    # TODO: remove test
    try:
        bot.send_message(message.chat.id, 'ok')
        karma_transaction(message.chat, 0, message.from_user, 10, 'test transaction')
        # bot.send_message(message.chat.id, json.dumps(users_cache, indent=4, separators=[', ', ': ']))
    except:
        crash_message(message)


@bot.message_handler(commands=['stat'])
def cmd_statistic(message):
    typing(message)
    try:
        if bool(message.reply_to_message):
            user = message.reply_to_message.from_user
        else:
            user = message.from_user
        karma = get_cached_user_karma(user.id, message.chat.id)

        # TODO: translate
        bot.reply_to(message, 'Статистика пользователя {user}:\nКарма: {karma}'.format(
            user=get_username_or_name(user),
            karma=karma
        ))
    except:
        crash_message(message)
