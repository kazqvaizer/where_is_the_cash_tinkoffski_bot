from datetime import datetime

import peewee as pw
from envparse import env
from telegram.update import Update

env.read_envfile()

db = pw.SqliteDatabase(env("DATABASE_URL"))


def _utcnow():
    return datetime.utcnow()


class BaseModel(pw.Model):
    created = pw.DateTimeField(default=_utcnow)
    modified = pw.DateTimeField(null=True)

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        if self.id is not None:
            self.modified = _utcnow()

        return super().save(*args, **kwargs)


class CashRemain(BaseModel):
    address = pw.CharField(unique=True)
    currency = pw.CharField()
    amount = pw.IntegerField()


class Chat(BaseModel):
    chat_id = pw.BigIntegerField(unique=True)
    chat_type = pw.CharField(null=True)
    username = pw.CharField(null=True)
    first_name = pw.CharField(null=True)
    last_name = pw.CharField(null=True)

    @classmethod
    def get_or_create_from_update(cls, update: Update) -> "Chat":
        chat_id = update.effective_chat.id
        defaults = dict(
            chat_type=update.effective_chat.type,
            username=update.effective_chat.username,
            first_name=update.effective_chat.first_name,
            last_name=update.effective_chat.last_name,
        )
        return cls.get_or_create(chat_id=chat_id, defaults=defaults)[0]


class Message(BaseModel):
    message_id = pw.IntegerField(null=True)
    chat = pw.ForeignKeyField(Chat, backref="messages")
    date = pw.DateTimeField(null=True)
    text = pw.CharField(null=True)

    @classmethod
    def create_from_update(cls, update: Update) -> "Message":
        return cls.create(
            chat=Chat.get_or_create_from_update(update),
            message_id=update.effective_message.message_id,
            date=update.effective_message.date,
            text=update.effective_message.text,
        )


app_models = BaseModel.__subclasses__()
