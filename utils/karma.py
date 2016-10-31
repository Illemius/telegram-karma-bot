import telebot
from config import LOGGING_CHAT
from meta import bot
from models.karma import Karma
from utils.cache import get_cached_user_chat, update_cached_user, reset_cache
from utils.chat import get_username_or_name
from .chat_logger import get_chat_logger

log = get_chat_logger(LOGGING_CHAT, 'karma')
KARMA_FIELD_NAME = 'karma'


def generate_karma_cache():
    # Karma.drop_collection()
    karma_records = Karma.objects.all()
    for karma in karma_records:
        if karma.rollback:
            continue
        if karma.from_user and karma.transfer:
            update_cached_user_karma(karma.from_user, karma.chat, -karma.amount)
        if karma.to_user:
            update_cached_user_karma(karma.to_user, karma.chat, karma.amount)


def regen_cache_for_user(user_id):
    # TODO: this
    pass


def update_cached_user_karma(user, chat, amount):
    user_data = get_cached_user_chat(user, chat)
    update_cached_user(user, chat, {KARMA_FIELD_NAME: user_data.get(KARMA_FIELD_NAME, 0) + amount})


def get_cached_user_karma(user, chat):
    user_data = get_cached_user_chat(user, chat)
    return user_data.get(KARMA_FIELD_NAME, 0)


def karma_transaction(chat=0, from_user=0, to_user=0, amount=0, description='', transfer=True):
    if type(chat) is telebot.types.Chat:
        chat_id = chat.id
    else:
        chat_id = chat

    if type(from_user) is telebot.types.User:
        from_user_id = from_user.id
    else:
        from_user_id = from_user

    if type(to_user) is telebot.types.User:
        to_user_id = to_user.id
    else:
        to_user_id = to_user

    if from_user and transfer:
        update_cached_user_karma(from_user_id, chat_id, -amount)
    if to_user:
        update_cached_user_karma(to_user_id, chat_id, amount)
    karma = Karma(chat=chat_id, from_user=from_user_id, to_user=to_user_id, amount=amount,
                  description=description, transfer=transfer)
    karma.save()
    log_transaction(karma.pk, chat=chat, from_user=from_user, to_user=to_user, amount=amount,
                    description=description, transfer=transfer)


def log_transaction(transaction, chat=0, from_user=0, to_user=0, amount=0, description='', transfer=True):
    try:
        if type(chat) is telebot.types.Chat:
            chat = chat
        else:
            chat = bot.get_chat(chat)
    except:
        chat = None

    try:
        if type(from_user) is telebot.types.User:
            from_user = from_user
        else:
            from_user = bot.get_chat(from_user)
    except:
        from_user = None

    try:
        if type(to_user) is telebot.types.User:
            to_user = to_user
        else:
            to_user = bot.get_chat(to_user)
    except:
        to_user = None

    message = ['#Transaction ID: <b>{}</b>'.format(transaction)]
    if chat:
        message.append('Dialog: {} (<code>{}</code>)'.format(chat.title or get_username_or_name(chat), chat.id))

    if from_user:
        message.append('From: {} (<code>{}</code>)'.format(get_username_or_name(from_user), from_user.id))
        if transfer:
            message.append(
                '\tResult amount: <i>{}</i>'.format(
                    get_cached_user_chat(from_user.id, chat.id).get(KARMA_FIELD_NAME, 0)))
    if to_user:
        message.append('To: {} (<code>{}</code>)'.format(get_username_or_name(to_user), to_user.id))
        message.append(
            '\tResult amount: <i>{}</i>'.format(get_cached_user_chat(to_user.id, chat.id).get(KARMA_FIELD_NAME, 0)))
    else:
        message.append('To: <code>/dev/null</code>')

    message.append('Description: <code>{}</code>'.format(description))
    message.append('Amount: <code>{}</code>'.format(amount))

    log.info('\n'.join(message))


def reset_chat_karma(chat):
    chat_karma = Karma.objects(chat=chat.id)

    counter = 0
    for karma in chat_karma:
        if not karma.rollback:
            karma.revoke()
            counter += 1

    reset_cache()
    generate_karma_cache()

    log.warning('Reset karma for chat: {} (<code>{}</code>)\n'
                '<code>{}</code> transactions'.format(chat.title or get_username_or_name(chat), chat.id,
                                                      counter))
    return counter
