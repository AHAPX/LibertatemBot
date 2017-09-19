import config
import validators
from commands.base import BaseCommand, BaseStep
from helpers import gen_token, get_content, get_logger
from models import Address, Post, Content


TEXT_PAY = 'send any amount of ethereum to post your message\n\nhttps://chart.googleapis.com/chart?chs=300x300&cht=qr&chl={}'
TEXT_ANON = 'your post will be anonymous, your name will not be stored in our database, but you cannot withdraw from post\'s balance'

logger = get_logger(__name__)


class PostCommand(BaseCommand):
    command = 'post'
    description = 'post new message'
    in_list = True
    args_template = [{
        'long': 'anon',
        'short': 'a',
        'help': TEXT_ANON,
    }]

    def run(self):
        self.send_message('write your post and send it')
        return (StepPost, self.kwargs)


class StepPost(BaseStep):
    def run(self, anon=False):
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
