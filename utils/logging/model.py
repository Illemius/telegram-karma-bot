from mongoengine import *


class BotLogs(Document):
    created = LongField()
    name = StringField()
    log_level = IntField()
    log_level_name = StringField()
    message = StringField()
    args = StringField()
    module = StringField()
    func_name = StringField()
    line_no = IntField()
    exception = StringField()
    process = LongField()
    thread = LongField()
    thread_name = StringField()
    session = StringField()
