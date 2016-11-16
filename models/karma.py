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

    def revoke(self):
        self.rollback = True
        self.save()

    def cancel(self):
        self.rollback = not self.rollback
        self.save()

    @classmethod
    def get_chat(cls, chat_id):
        return Karma.objects(chat=chat_id)

    @classmethod
    def get_chat_karma(cls, chat_id):
        karma_records = Karma.get_chat(chat_id)
        print(len(karma_records))
        result = {}
        for karma in karma_records:
            if karma.rollback:
                continue
            if karma.from_user and karma.transfer:
                result[karma.from_user] = result.get(karma.from_user, 0) - karma.amount
            if karma.to_user:
                result[karma.to_user] = result.get(karma.to_user, 0) + karma.amount
        return result
