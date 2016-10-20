import datetime
from mongoengine import Document, DateTimeField

from meta import TIMEZONE


class BaseModel(Document):
    # Logging
    creation_date = DateTimeField(default=datetime.datetime.now)
    modified_date = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        if not self.creation_date:
            self.creation_date = datetime.datetime.now(TIMEZONE)
        self.modified_date = datetime.datetime.now(TIMEZONE)
        return super(BaseModel, self).save(*args, **kwargs)
