import datetime

from peewee import *

import config
from coins import gen_wallet


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
    text = TextField()
    forward_chat_id = CharField(null=True)
    forward_message_id = CharField(null=True)
    token = CharField()
    balance = FloatField(default=0)
    is_deleted = BooleanField(default=False)
    address = ForeignKeyField(Address, related_name='post', on_delete='SET NULL')
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


class Reaction(Model):
    user = CharField(null=True)
    post = ForeignKeyField(Post, related_name='reactions', on_delete='SET NULL')
    is_like = BooleanField(default=True)
    amount = FloatField(null=True)
    address = ForeignKeyField(Address, related_name='reaction', on_delete='SET NULL')
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = config.DB


class Settings(Model):
    user = CharField(null=True)
    address = CharField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = config.DB


if __name__ == '__main__':
    config.DB.connect()
    TABLES = [Address, Post, Reaction, Settings]
    added = []
    for table in TABLES:
        if not table.table_exists():
            config.DB.create_tables([table])
            added.append(table.__name__)
    if added:
        print('Tables created: {}'.format(', '.join(added)))
    else:
        print('All tables already exist')
