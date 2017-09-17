import config
import validators
from commands.base import BaseCommand, BaseStep
from helpers import post_message, add_react
from models import Address, Post, Reaction


class ConfirmCommand(BaseCommand):
    command = 'confirm'
    description = 'confirm payment'
    is_debug = True
    args_template = [{
        'long': 'like',
        'short': 'l',
        'help': 'confirm like',
    }, {
        'long': 'dislike',
        'short': 'd',
        'help': 'confirm dislike',
    }]

    def run(self):
        if self.kwargs.get('like'):
            entity = Reaction
            try:
                entity_id = Reaction.select().join(Address).\
                    where(
                        Address.is_accepted == False,
                        Reaction.is_like == True
                    ).\
                    order_by(Reaction.created_at.desc()).\
                    limit(1)[0].id
            except:
                self.send_message('no likes')
                return
        elif self.kwargs.get('dislike'):
            entity = Reaction
            try:
                entity_id = Reaction.select().join(Address).\
                    where(
                        Address.is_accepted == False,
                        Reaction.is_like == False
                    ).\
                    order_by(Reaction.created_at.desc()).\
                    limit(1)[0].id
            except:
                self.send_message('no likes')
                return
        else:
            entity = Post
            try:
                entity_id = Post.select().join(Address).\
                    where(
                        Address.is_accepted == False,
                        Post.is_deleted == False
                    ).\
                    order_by(Post.created_at.desc()).\
                    limit(1)[0].id
            except:
                self.send_message('not posts')
                return
        self.send_message('how much to send?')
        return (ConfirmStep, {'entity_id': entity_id, 'entity': entity})


class ConfirmStep(BaseStep):
    validator = validators.Float
    valid_name = 'amount'

    def run(self, amount, entity, entity_id):
        try:
            item = entity.get(entity.id == entity_id)
        except entity.DoesNotExist:
            self.send_message('not found')
            return
        with config.DB.atomic() as tnx:
            try:
                if isinstance(item, Post):
                    post_message(item, amount)
                elif isinstance(item, Reaction):
                    add_react(item, amount)
                item.address.is_accepted = True
                item.address.balance = amount
                item.address.save()
                tnx.commit()
            except Exception as e:
                tnx.rollback()
