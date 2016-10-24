import time

from TranslateLib import bool_to_str, translate as _

from config import ANTI_FLOOD_TIMEOUT
from meta import bot, bot_id
from models.karma import Karma
from utils import karma_votes_calculator
from utils.cache import update_cached_user, get_cached_user_chat
from utils.chat import crash_message, get_username_or_name, typing, get_dialog_object
from utils.karma import generate_karma_cache, karma_transaction, get_cached_user_karma, log

generate_karma_cache()
KARMA_CHANGE_REGEX = '^(?P<vote>[+\-]{2,})(?P<description>.+)?'


def vote_message(message, description='', amount=1):
    # TODO: anti spam
    if bool(message.reply_to_message) and message.reply_to_message.from_user.id != message.from_user.id:
        user_cache = get_cached_user_chat(message.from_user.id, message.chat.id)
        last_message = user_cache.get('last_message', 0)
        timeout = user_cache.get('karma_change_timeout', ANTI_FLOOD_TIMEOUT)
        warn_count = user_cache.get('karma_change_warn', 0) + 1
        update_cached_user(message.from_user.id, message.chat.id, {
            'last_message': time.time(),
            'karma_change_timeout': time.time() - last_message + ANTI_FLOOD_TIMEOUT * warn_count,
            'karma_change_warn': warn_count
        })
        if time.time() - last_message < timeout:
            log.warning(
                '#flood {user} (<code>{user_id}</code>) is flooding <b>x{count}</b>!\n'
                'Chat "{chat}" (<code>{chat_id}</code>)\n'
                'Set timeout: {timeout:.1f}'.format(
                    user=get_username_or_name(message.from_user),
                    user_id=message.from_user.id,
                    count=warn_count,
                    chat=message.chat.title,
                    chat_id=message.chat.id,
                    timeout=get_cached_user_chat(message.from_user.id, message.chat.id).get('karma_change_timeout',
                                                                                            ANTI_FLOOD_TIMEOUT)
                ))
            return bot.reply_to(message, _('anti spam karma {timeout:.0f}s')
                                .format(timeout=timeout - (time.time() - last_message)))
        update_cached_user(message.from_user.id, message.chat.id, {'karma_change_timeout': ANTI_FLOOD_TIMEOUT,
                                                                   'karma_change_warn': 0})

        karma_transaction(message.chat, message.from_user, message.reply_to_message.from_user,
                          amount=amount,
                          description=bool_to_str(amount > 0, 'good message', 'bad message'),
                          transfer=False)
        user = get_dialog_object(message.reply_to_message.from_user.id)

        if user.subscribe or True:
            try:
                if amount > 0:
                    text = _('{user} thanked you chatting {chat}', locale=user.locale)
                elif amount < 0:
                    text = _('{user} did not like your message in the chat {chat}', locale=user.locale)
                else:
                    text = _('User {user} is indifferent to your message in the chat {chat}', locale=user.locale)

                if len(description):
                    text += '\n' + _('Comment: {text}')
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


def exec_vote_cmd(message, amount):
    try:
        description_pos = 0
        for messageEntity in message.entities:
            if messageEntity.type == 'bot_command':
                description_pos = messageEntity.offset + messageEntity.length
                break
        description = message.text[description_pos:]
        vote_message(message, description, amount)
    except:
        return crash_message(message)


@bot.message_handler(commands=['good', 'tnx', 'thanks'])
def cmd_tnx(message):
    typing(message)
    exec_vote_cmd(message, 1)


@bot.message_handler(commands=['bad'])
def cmd_bad(message):
    typing(message)
    exec_vote_cmd(message, -1)


@bot.message_handler(regexp=KARMA_CHANGE_REGEX)
def cmd_vote_symbols(message):
    try:
        amount, description = karma_votes_calculator.parse_message(message.text)
        vote_message(message, description, amount)
    except:
        crash_message(message)


@bot.message_handler(func=lambda message: message.text.startswith('🍪'), content_types=['text'])
def cmd_cookie(message):
    try:
        amount = 0
        for symbol in message.text:
            if symbol == '🍪':
                amount += 1
        amount = karma_votes_calculator.calculate_karma_amount(amount)
        vote_message(message, amount=amount)
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


@bot.message_handler(commands=['top'])
def cmd_top(message):
    try:
        karma_records = Karma.objects(chat=message.chat.id)
        users = {}
        for karma in karma_records:
            if karma.rollback:
                continue
            if karma.from_user and karma.transfer:
                users[karma.from_user] = users.get(karma.from_user, 0) + karma.amount
            if karma.to_user:
                users[karma.to_user] = users.get(karma.to_user, 0) + karma.amount

        text = ['Статистика:']

        index = 0
        for user, karma in sorted(users.items(), key=lambda x: x[1], reverse=True):
            if user == bot_id:
                continue
            index += 1
            text.append('{}) {}: {}'.format(index, get_username_or_name(bot.get_chat(user)), karma))
        bot.send_message(message.chat.id, '\n'.join(text))
    except:
        crash_message(message)
