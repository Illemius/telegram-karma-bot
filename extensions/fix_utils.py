from config import ROOT_UID
from meta import bot
from models.messages import Messages
from utils.chat import crash_message
from utils.karma import log


@bot.message_handler(commands=['fix_messages'])
def cmd_fix_messages(message):
    """
    Add field 'is_command' to Messages document.
    :param message:
    :return:
    """
    try:
        if not message.from_user.id == ROOT_UID:
            return

        messages = Messages.objects.all()
        messages.update(set__is_command=False)
        log.info('Fixed {} messages.'.format(len(messages)))
        bot.reply_to(message, 'Fixed {} messages.'.format(len(messages)))
    except:
        crash_message(message)
