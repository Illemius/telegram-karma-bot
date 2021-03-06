import re
import sys
import time
from datetime import datetime, timedelta

from TranslateLib import bool_to_str, translate as _
from TranslateLib import get_num_ending

from config import ANTI_FLOOD_TIMEOUT, LOGGING_CHAT
from meta import bot, bot_id, TIMEZONE
from models.dialogs import AdminSubscribe
from models.karma import Karma
from models.messages import Messages
from utils import karma_votes_calculator
from utils.cache import update_cached_user, get_cached_user_chat
from utils.chat import crash_message, get_username_or_name, typing, get_dialog_object, get_chat_url_or_title, \
    sender_is_admin, parse_inline_data, is_private
from utils.karma import generate_karma_cache, karma_transaction, get_cached_user_karma, log, reset_chat_karma, \
    notify_chat_admins
from utils.karma_votes_calculator import KARMA_CHANGE_REGEX
from utils.logging import CrashReport

generate_karma_cache()


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

        if user.subscribe:
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
                    chat=get_chat_url_or_title(message),
                    text=description
                ), disable_web_page_preview=True, parse_mode='markdown')
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


@bot.callback_query_handler(func=lambda callbackquery: parse_inline_data(callbackquery.data)[0] == 'CANCEL_TRANSACTION')
def query_settings(callbackquery):
    try:
        key, data = parse_inline_data(callbackquery.data)

        karma = Karma.get_transaction(data[0])
        if karma:
            if not sender_is_admin(karma.chat, callbackquery.from_user.id):
                return bot.answer_callback_query(callbackquery.id, 'You shall not pass!')

            karma.cancel()
            if karma.rollback:
                bot.answer_callback_query(callbackquery.id, 'Transaction ' + data[0] + ' is canceled!')
                text = '#karma #WARNING #Transaction\nCanceled: #{}\nby {} ({})'.format(
                    data[0], get_username_or_name(callbackquery.from_user), callbackquery.from_user.id)
                bot.send_message(LOGGING_CHAT, text)
                notify_chat_admins(karma.chat, text)
            else:
                bot.answer_callback_query(callbackquery.id, 'Transaction ' + data[0] + ' is activated!')
                text = '#karma #WARNING #Transaction\nRestored: #{}\nby {} ({})'.format(
                        data[0], get_username_or_name(callbackquery.from_user), callbackquery.from_user.id)
                bot.send_message(LOGGING_CHAT, text)
                notify_chat_admins(karma.chat, text)

        bot.answer_callback_query(callbackquery.id, 'Wrong transaction!')
    except:
        with CrashReport(*sys.exc_info()) as c:
            log.warning(c.formatted_traceback)
            c.save()


@bot.message_handler(commands=['like', 'good', 'tnx', 'thanks'])
def cmd_tnx(message):
    exec_vote_cmd(message, 1)


@bot.message_handler(commands=['bad'])
def cmd_bad(message):
    exec_vote_cmd(message, -1)


def check_karma_change_regex(message):
    if message.content_type != 'text':
        return False

    text = message.text.replace('—', '--')
    if re.match(KARMA_CHANGE_REGEX, text):
        return True
    return False


@bot.message_handler(func=check_karma_change_regex)
def cmd_vote_symbols(message):
    try:
        amount, description = karma_votes_calculator.parse_message(message.text)
        vote_message(message, description, amount)
    except:
        crash_message(message)


@bot.message_handler(commands=['statistic', 'stat'])
def cmd_statistic(message):
    try:
        typing(message)
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
        typing(message)
        karma_records = Karma.objects(chat=message.chat.id)
        users = {}
        for karma in karma_records:
            if karma.rollback:
                continue
            if karma.from_user and karma.transfer:
                users[karma.from_user] = users.get(karma.from_user, 0) - karma.amount
            if karma.to_user:
                users[karma.to_user] = users.get(karma.to_user, 0) + karma.amount

        text = ['Статистика:']

        if bot_id in users:
            users.pop(bot_id)

        for index, (user, karma) in enumerate(sorted(users.items(), key=lambda x: x[1], reverse=True), start=1):
            if index > 10:
                break
            text.append('{}) {}: {}'.format(index, get_username_or_name(bot.get_chat(user)), karma))
        bot.send_message(message.chat.id, '\n'.join(text), disable_notification=True)
    except:
        crash_message(message)


@bot.message_handler(commands=['rs', 'reset'])
def cmd_reset_chat(message):
    try:
        typing(message)
        if is_private(message) or not sender_is_admin(message.chat.id, message.from_user.id):
            return None

        reset = reset_chat_karma(message.chat)
        if reset:
            bot.reply_to(message, get_num_ending(reset, ('Отменена {} транзакция.',
                                                         'Отменено {} транзакции.',
                                                         'Отменено {} транзакций.')).format(reset))
        else:
            bot.reply_to(message, 'Нечего отменять.')
    except:
        crash_message(message)


@bot.message_handler(commands=['core_stat'])
def cmd_core_stat(message):
    try:
        if is_private(message) or not sender_is_admin(message.chat.id, message.from_user.id):
            return None
        typing(message)

        karma_objects = Karma.objects(chat=message.chat.id)
        transactions = 0
        users = []
        canceled = 0
        canceled_amount = 0
        amount = 0

        for karma in karma_objects:
            transactions += 1
            amount += karma.amount
            if karma.to_user not in users:
                users.append(karma.to_user)
            if karma.from_user not in users:
                users.append(karma.from_user)
            if karma.rollback:
                canceled += 1
                canceled_amount += karma.amount

        bot.reply_to(
            message,
            'Транзакций: {} (отменено: {}, активно: {})\n'
            'Пользователей: {}\n'
            'Карма в чате: {} (отменено {}, активно {})\n'.format(
                transactions, canceled, transactions - canceled,
                len(users),
                amount, canceled_amount, amount - canceled_amount
            )
        )
    except:
        crash_message(message)


@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    try:
        typing(message)
        if message.chat.type == 'private':
            return bot.reply_to(message, 'Доступно только в груповых диалогах')

        if not bool(message.reply_to_message) or message.reply_to_message.from_user.id == message.from_user.id:
            return bot.reply_to(message, 'Нельзя переводить карму себе же.')

        amount_pos = 0
        for messageEntity in message.entities:
            if messageEntity.type == 'bot_command':
                amount_pos = messageEntity.offset + messageEntity.length
                break
        amount = message.text[amount_pos:].strip()

        if not amount.isdigit():
            return bot.reply_to(message, 'Не верная сумма перевода')

        amount = abs(int(amount))

        if amount == 0:
            return bot.reply_to(message, 'Сумма перевода должна біть больше нуля')

        from_user_karma = get_cached_user_karma(message.from_user.id, message.chat.id)

        if amount > from_user_karma:
            return bot.reply_to(message, 'Нельзя переводить больше, чем карма отправителя.')

        karma_transaction(message.chat, message.from_user, message.reply_to_message.from_user, amount, 'transfer')
    except:
        crash_message(message)


@bot.message_handler(commands=['apay'])
def cmd_admin_pay(message):
    try:
        if is_private(message) or not sender_is_admin(message.chat.id, message.from_user.id):
            return None

        if not bool(message.reply_to_message):
            return None

        typing(message)

        amount_pos = 0
        for messageEntity in message.entities:
            if messageEntity.type == 'bot_command':
                amount_pos = messageEntity.offset + messageEntity.length
                break
        amount = message.text[amount_pos:].strip()

        if amount.startswith('-'):
            minus = True
            amount = amount.replace('-', '')
        else:
            minus = False

        if not amount.isdigit():
            return bot.reply_to(message, 'Не верная сумма перевода')

        amount = -int(amount) if minus else int(amount)

        karma_transaction(message.chat, message.from_user, message.reply_to_message.from_user, amount,
                          'admin transfer', transfer=False)
    except:
        crash_message(message)


@bot.message_handler(commands=['messages'])
def cmd_messages_count(message):
    try:
        typing(message)
        date = datetime.now(TIMEZONE) - timedelta(days=1)
        users = Messages.calculate(message.chat.id, date)

        text = ['Топ флудеров за последние 24 часа:']

        if bot_id in users:
            users.pop(bot_id)

        for index, (user, karma) in enumerate(sorted(users.items(), key=lambda x: x[1], reverse=True), start=1):
            if index > 10:
                break
            text.append('{}) {}: {} сбщ.'.format(index, get_username_or_name(bot.get_chat(user)), karma))
        bot.send_message(message.chat.id, '\n'.join(text), disable_notification=True)
    except:
        crash_message(message)


@bot.message_handler(commands=['asubscribe'])
def cmd_admin_subscribe(message):
    if message.location == 'private':
        return None

    if not sender_is_admin(message.chat.id, message.from_user.id):
        return None

    if AdminSubscribe.is_subscribed(message.chat.id, message.from_user.id):
        return bot.reply_to(message, 'Вы уже подписаны на уведомления об обновлениях кармы в этом диалоге')

    AdminSubscribe.subscribe(message.chat.id, message.from_user.id)
    bot.reply_to(message, 'Вы подписались на уведомления об изменениях кармы в этом диалоге')


@bot.message_handler(commands=['aunsubscribe'])
def cmd_admin_unsubscribe(message):
    if message.location == 'private':
        return None

    if AdminSubscribe.is_subscribed(message.chat.id, message.from_user.id):
        AdminSubscribe.unsubscribe(message.chat.id, message.chat.id)
        bot.reply_to(message, 'Вы отписались от уведомлений об изменении кармы в этом чате.')
