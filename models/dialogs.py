import datetime

from mongoengine import *

from config import DEFAULT_LOCALE
from meta import TIMEZONE


class Dialogs(Document):
    # Key
    index = IntField()

    # Dialog settings
    locale = StringField(default=DEFAULT_LOCALE)
    admin = BooleanField(default=False)

    # For users
    default_dialog = IntField()
    subscribe = BooleanField(default=False)

    # Logging
    creation_date = DateTimeField(default=datetime.datetime.now)
    modified_date = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        if not self.creation_date:
            self.creation_date = datetime.datetime.now(TIMEZONE)
        self.modified_date = datetime.datetime.now(TIMEZONE)
        return super(Dialogs, self).save(*args, **kwargs)


class AdminSubscribe(Document):
    user_id = IntField()
    chat_id = IntField()

    # Logging
    creation_date = DateTimeField(default=datetime.datetime.now)
    modified_date = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        if not self.creation_date:
            self.creation_date = datetime.datetime.now(TIMEZONE)
        self.modified_date = datetime.datetime.now(TIMEZONE)
        return super(AdminSubscribe, self).save(*args, **kwargs)

    @classmethod
    def subscribe(cls, chat_id, user_id):
        if len(AdminSubscribe.objects(chat_id=chat_id, user_id=user_id)) > 0:
            return False
        AdminSubscribe(chat_id=chat_id, user_id=user_id).save()
        return True

    @classmethod
    def unsubscribe(cls, chat_id, user_id):
        adminsubscribes = AdminSubscribe.objects(chat_id=chat_id, user_id=user_id)
        for adminsubscribe in adminsubscribes:
            adminsubscribe.delete()
            return True
        return False

    @classmethod
    def is_subscribed(cls, chat_id, user_id):
        if len(AdminSubscribe.objects(chat_id=chat_id, user_id=user_id)) > 0:
            return True
        return False

    @classmethod
    def get_chat_subscribers(cls, chat_id):
        return [int(adminsubscribe.user_id) for adminsubscribe in AdminSubscribe.objects(chat_id=chat_id)]
