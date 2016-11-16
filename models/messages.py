import datetime

from mongoengine import *

from meta import TIMEZONE


class Messages(Document):
    # TODO: messages statistic
    chat = IntField()
    user = IntField()
    content_type = StringField()

    # Logging
    creation_date = DateTimeField(default=datetime.datetime.now)
    modified_date = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        if not self.creation_date:
            self.creation_date = datetime.datetime.now(TIMEZONE)
        self.modified_date = datetime.datetime.now(TIMEZONE)
        return super(Messages, self).save(*args, **kwargs)

    @classmethod
    def add(cls, chat, user, content_type):
        Messages(chat=chat, user=user, content_type=content_type).save()

    @classmethod
    def calculate(cls, chat_id=None, time=None):
        payload = {}
        if chat_id:
            payload['chat'] = chat_id
        if time:
            payload['creation_date__gt'] = time
        messages = Messages.objects(**payload)
        users = {}
        for msg in messages:
            users[msg.user] = users.get(msg.user, 0) + 1
        return users
