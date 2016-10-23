from TranslateLib import translate as _, get_locales_list, get_locale

import telebot
from meta import bot
from utils.chat import ParseUserData, get_username_or_name, typing, cant_send_private, generate_inline_data, \
    crash_message, parse_inline_data, get_dialog_object


@bot.message_handler(commands=['help'])
def cmd_help(message):
    pass


@bot.message_handler(commands=['start'])
@ParseUserData
def cmd_start(message, user, chat):
    typing(message)
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, _('hello {user_name}', locale=user.locale)
                         .format(user_name=get_username_or_name(message.from_user)))


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
