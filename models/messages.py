import datetime

from mongoengine import *

from meta import TIMEZONE
from utils.karma import log


class Messages(Document):
    # TODO: messages statistic
    chat = IntField()
    user = IntField()
    content_type = StringField()
    is_command = BooleanField(default=False)

    # Logging
    creation_date = DateTimeField(default=datetime.datetime.now)
    modified_date = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        if not self.creation_date:
            self.creation_date = datetime.datetime.now(TIMEZONE)
        self.modified_date = datetime.datetime.now(TIMEZONE)
        return super(Messages, self).save(*args, **kwargs)

    @classmethod
    def add(cls, chat, user, content_type, text):
        if bool(text) and text.startswith('/'):
            is_command = True
        else:
            is_command = False

        Messages(chat=chat, user=user, content_type=content_type, is_command=is_command).save()

    @classmethod
    def calculate(cls, chat_id=None, time=None, with_commands=False):
        payload = {}
        if chat_id:
            payload['chat'] = chat_id
        if time:
            payload['creation_date__gt'] = time
        if not with_commands:
            payload['is_command'] = False
        messages = Messages.objects(**payload)
        users = {}
        for msg in messages:
            users[msg.user] = users.get(msg.user, 0) + 1
        return users
