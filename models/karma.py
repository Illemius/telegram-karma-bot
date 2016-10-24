import datetime

from mongoengine import *

from meta import TIMEZONE


class Karma(Document):
    chat = IntField()
    from_user = IntField(default=0)
    to_user = IntField(default=0)

    amount = IntField()
    transfer = BooleanField()
    description = StringField()

    rollback = BooleanField()

    # Logging
    creation_date = DateTimeField(default=datetime.datetime.now)
    modified_date = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        if not self.creation_date:
            self.creation_date = datetime.datetime.now(TIMEZONE)
        self.modified_date = datetime.datetime.now(TIMEZONE)
        return super(Karma, self).save(*args, **kwargs)
