import config
import validators
from commands.base import BaseCommand, BaseStep
from helpers import gen_token, get_content, get_logger
from models import Address, Post, Content


TEXT_PAY = 'send any amount of ethereum to post your message\n\nhttps://chart.googleapis.com/chart?chs=300x300&cht=qr&chl={}'
TEXT_ANON = 'your post will be anonymous, your name will not be stored in our database, but you cannot withdraw from post\'s balance'
TEXT_FORWARD = 'your message will be forwarded to channel with your name'

logger = get_logger(__name__)


class PostCommand(BaseCommand):
    command = 'post'
    description = 'post new message'
    in_list = True
    args_template = [{
        'long': 'anon',
        'short': 'a',
        'help': TEXT_ANON,
    }, {
        'long': 'forward',
        'short': 'f',
        'help': TEXT_FORWARD,
    }]

    def run(self):
        if self.kwargs.get('anon') and self.kwargs.get('forward'):
            self.send_message('you cannot post anonymous message as forwarded message')
            return
        self.send_message('write your post and send it')
        return (StepPost, self.kwargs)


class StepPost(BaseStep):
    def run(self, anon=False, forward=False):
        try:
            data = get_content(self.message)
        except ContentError as e:
            self.send.message(e)
        with config.DB.atomic() as tnx:
            try:
                content = Content.create(type=data[0], text=data[1], file_id=data[2])
                post = Post(
                    content=content,
                    token=gen_token(),
                    address=Address.new()
                )
                if not anon:
                    post.user = self.user_id
                if forward:
                    if self.message.forward_from:
                        self.send_message('you cannot forward messages for forward posting, write your message')
                        return (type(self), {'forward': forward})
                    post.forward_message_id = self.message.message_id
                    post.created_at = self.message.date
                post.save()
                if str(self.user_id) == config.ADMIN_ID and config.ADMIN_DEFAULT_BALANCE > 0 and not config.DEBUG:
                    post.send(config.ADMIN_DEFAULT_BALANCE, bot=self.bot)
                    post.address.is_accepted = True
                    post.address.save()
                    self.send_message('message posted')
                else:
                    self.send_message(TEXT_PAY.format(post.address.address))
                    self.send_message(post.address.address)
                tnx.commit()
            except Exception as e:
                logger.error(e)
                tnx.rollback()
