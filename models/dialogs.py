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
