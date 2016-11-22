from TranslateLib import translate as _

from meta import bot
from models.dialogs import Dialogs
from utils.chat import ParseUserData, get_username_or_name, typing, crash_message


@bot.message_handler(commands=['help'])
def cmd_help(message):
    text = [
        'Я - бот, который считает карму в чатах Telegram',
        '',
        'Список моих команд:',
        '/like - "Лайкнуть" сообщение',
        '/bad - "Дизлайкнуть" сообщение',
        '/stat - Отобразить статистику пользователя',
        '/messages - Статистика сообщений в диалоге',
        '/top - Топ пользователей по карме',
        '/subscribe - Подписаться на обновления об изменениях кармы',
        '/unsubscribe - Отписаться от обновлений об изменении кармы',
        '',
        'Так же для изменения кармы можно использовать символы "++" и "--" а так же смайлы "🍪, 💩, 👍🏻, 👎🏻"',
        'Бем больше повтора символов в сообщении, тем на большую сумму будут изменена карма!'
    ]
    bot.reply_to(message, '\n'.join(text))


@bot.message_handler(commands=['ahelp'])
def cmd_ahelp(message):
    text = [
        '',
    ]
    bot.reply_to(message, '\n'.join(text))


@bot.message_handler(commands=['start'])
@ParseUserData
def cmd_start(message, user, chat):
    typing(message)
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, _('hello {user_name}', locale=user.locale)
                         .format(user_name=get_username_or_name(message.from_user)))


"""
@bot.message_handler(commands=['settings'])
@ParseUserData
def cmd_settings(message, user, chat):
    try:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(
            _('locale settings', locale=user.locale),
            callback_data=generate_inline_data('settings', ['locale'])
        ))
        bot.send_message(message.from_user.id, _('settings', locale=user.locale), reply_markup=markup)
    except:
        crash_message(message)
        cant_send_private(message, chat.locale)
    else:
        if message.chat.type != 'private':
            bot.reply_to('keyboard settings sent to your private messages')


@bot.callback_query_handler(func=lambda callbackquery: parse_inline_data(callbackquery.data)[0] == 'settings')
def query_settings(callbackquery):
    try:
        key, data = parse_inline_data(callbackquery.data)
        dialog = get_dialog_object(callbackquery.from_user.id)
        if data[0] == 'locale':
            if len(data) == 2:
                dialog.locale = data[1]
                dialog.save()
                bot.edit_message_text(_('settings updated. new locale is {locale}', locale=dialog.locale).format(
                    locale=get_locale(data[1]).get_short_name() or data[1]),
                    callbackquery.message.chat.id,
                    callbackquery.message.message_id)
                return
            locales = get_locales_list()
            markup = telebot.types.InlineKeyboardMarkup()
            for locale in locales:
                title = locale
                try:
                    loc = get_locale(locale)
                except NameError:
                    pass
                else:
                    title = loc.get_short_name()
                markup.add(telebot.types.InlineKeyboardButton(
                    title, callback_data=generate_inline_data('settings', ['locale', locale])
                ))
            bot.edit_message_text(_('chose locale', locale=dialog.locale),
                                  callbackquery.message.chat.id,
                                  callbackquery.message.message_id,
                                  reply_markup=markup)
            return
    except:
        crash_message(callbackquery.message)
"""


@bot.message_handler(commands=['subscribe'])
def cmd_subscribe(message):
    try:
        user_objects = Dialogs.objects(index=message.from_user.id)
        if len(user_objects) > 0:
            user = user_objects[0]
        else:
            user = Dialogs(index=message.from_user.id)

        if not user.subscribe:
            user.subscribe = True
            user.save()
            try:
                bot.send_message(message.from_user.id, 'Теперь Вам будут приходить уведомления об изменении кармы.')
                if message.location != 'private':
                    bot.reply_to(message, 'Теперь Вам будут приходить уведомления об изменении кармы.')
            except:
                bot.reply_to(message, 'Сначала напиши мне в ЛС.')
        else:
            bot.reply_to(message, 'Вы уже подписаны на уведомления об изменении кармы.')
    except:
        crash_message(message)


@bot.message_handler(commands=['unsubscribe'])
def cmd_unsubscribe(message):
    try:
        user_objects = Dialogs.objects(index=message.from_user.id)
        if len(user_objects) > 0:
            user = user_objects[0]
        else:
            user = Dialogs(index=message.from_user.id)
            user.save()
        if user.subscribe:
            user.subscribe = False
            user.save()
            bot.reply_to(message, 'Вы отписались от уведомлений об изменении кармы.')
        else:
            bot.reply_to(message, 'Вы не подписаны на уведомления об изменении кармы.')
    except:
        crash_message(message)
