import datetime

import peeweedbevolve
from peewee import *

import config
import consts
from coins import gen_wallet
from helpers import get_bot, send_message


CONTENT_CHOICES = (
    (consts.CONTENT_TEXT, 'text'),
    (consts.CONTENT_PHOTO, 'photo'),
    (consts.CONTENT_AUDIO, 'audio'),
    (consts.CONTENT_VOICE, 'voice'),
    (consts.CONTENT_VIDEO, 'video'),
    (consts.CONTENT_STICKER, 'sticker'),
)


class Content(Model):
    type = IntegerField(choices=CONTENT_CHOICES, default=consts.CONTENT_TEXT)
    text = TextField(null=True)
    file_id = CharField(null=True)

    class Meta:
        database = config.DB


class Address(Model):
    address = CharField()
    balance = FloatField(default=0)
    addr_id = CharField(null=True)
    is_accepted = BooleanField(default=False)
    is_cancelled = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        super(Address, self).save(*args, **kwargs)

    @classmethod
    def new(cls):
        wallet = gen_wallet()
        return cls.create(address=wallet.address, addr_id=wallet.id)

    class Meta:
        database = config.DB


class Post(Model):
    user = CharField(null=True)
    message_id = IntegerField(null=True)
    content = ForeignKeyField(Content, related_name='post', on_delete='SET NULL', null=True)
    text = TextField(null=True)
    forward_chat_id = CharField(null=True)
    forward_message_id = CharField(null=True)
    token = CharField()
    balance = FloatField(default=0)
    is_deleted = BooleanField(default=False)
    address = ForeignKeyField(Address, related_name='post', on_delete='SET NULL', null=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = config.DB

    def get_full_balance(self):
        likes = sum([r.amount for r in self.reactions.join(Address).where(
            Reaction.is_like == True,
            Address.is_accepted == True,
            Reaction.amount > 0
        )])
        dislikes = sum([r.amount for r in self.reactions.join(Address).where(
            Reaction.is_like == False,
            Address.is_accepted == True,
            Reaction.amount > 0
        )])
        return '={}(+{} -{})'.format(self.balance, likes, dislikes)

    def send(self, balance, bot=None):
        bot = bot or get_bot()
        if self.forward_chat_id and self.forward_message_id:
            message = bot.forward_message(
                chat_id=config.CHANNEL_NAME,
                from_chat_id=self.forward_chat_id,
                message_id=self.forward_message_id
            )
        else:
            if self.content.type == consts.CONTENT_PHOTO:
                message = bot.send_photo(config.CHANNEL_NAME, photo=self.content.file_id)
            elif self.content.type == consts.CONTENT_AUDIO:
                message = bot.send_audio(config.CHANNEL_NAME, audio=self.content.file_id)
            elif self.content.type == consts.CONTENT_VOICE:
                message = bot.send_voice(config.CHANNEL_NAME, voice=self.content.file_id)
            elif self.content.type == consts.CONTENT_VIDEO:
                message = bot.send_video(config.CHANNEL_NAME, video=self.content.file_id)
            elif self.content.type == consts.CONTENT_STICKER:
                message = bot.send_sticker(config.CHANNEL_NAME, sticker=self.content.file_id)
            else:
                message = bot.send_message(config.CHANNEL_NAME, text=self.content.text, parse_mode='Markdown')
        self.balance = balance
        self.message_id = message.message_id
        self.save()
        if self.user:
            send_message(bot, int(self.user), text='your message was posted')


class Reaction(Model):
    user = CharField(null=True)
    post = ForeignKeyField(Post, related_name='reactions', on_delete='SET NULL')
    is_like = BooleanField(default=True)
    amount = FloatField(null=True)
    address = ForeignKeyField(Address, related_name='reaction', on_delete='SET NULL')
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = config.DB

    def send(amount, bot=None):
        bot = bot or get_bot()
        name = 'like' if self.is_like else 'dislike'
        self.amount = amount
        self.save()
        if self.is_like:
            self.post.balance += amount
        else:
            self.post.balance -= amount
        if self.post.balance <= 0:
            self.post.is_deleted = True
        self.post.save()
        if self.user:
            send_message(bot, int(self.user), text='your {} accepted'.format(name))
        if self.post.user:
            send_message(bot, int(self.post.user), text='your post received {} for {}ETH'.format(name, self.amount))
# TODO: what if delete return error, but db already changed
        if self.post.balance <= 0:
            bot.delete_message(chat_id=config.CHANNEL_NAME, message_id=self.post.message_id)
            if self.post.user:
                send_message(bot, int(self.post.user), text='your post was deleted')


class Settings(Model):
    user = CharField(null=True)
    address = CharField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = config.DB


if __name__ == '__main__':
    config.DB.connect()
    config.DB.evolve()
