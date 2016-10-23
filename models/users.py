from mongoengine import *
from .base_model import BaseModel


class Users(BaseModel):
    # Key
    user_id = IntField()

    # Settings
    locale = StringField()
    default_dialog = IntField()
    admin = BooleanField(default=False)


class Dialogs(BaseModel):
    chat_id = IntField()
    locale = StringField()
