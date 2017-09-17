import config
import validators
from commands.base import BaseCommand, BaseStep
from helpers import gen_token, post_message
from models import Address, Post


TEXT_PAY = 'send any amount of ethereum to post your message\n\nhttps://chart.googleapis.com/chart?chs=300x300&cht=qr&chl={}'
TEXT_ANON = 'your post will be anonymous, your name will not be stored in our database, but you cannot withdraw from post\'s balance'


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
    validator = validators.Str
    valid_name = 'text'

    def run(self, text, anon=False):
        post = Post(
            text=text,
            token=gen_token(text),
            address=Address.new()
        )
        if not anon:
            post.user = self.user_id
#        if forward:
#            post.forward_chat_id = self.message.chat_id
#            post.forward_message_id = self.message.message_id
        post.save()
        if str(self.user_id) == config.ADMIN_ID and config.ADMIN_DEFAULT_BALANCE > 0 and not config.DEBUG:
            post_message(post, config.ADMIN_DEFAULT_BALANCE, bot=self.bot)
            post.address.is_accepted = True
            post.address.save()
            self.send_message('message posted')
        else:
            self.send_message(TEXT_PAY.format(post.address.address))
            self.send_message(post.address.address)
