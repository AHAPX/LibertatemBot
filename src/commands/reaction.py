from commands.base import BasePostCommand, BasePostEntryStep
from models import Address, Reaction


TEXT_PAY = 'send any amount of ethereum to {} the post\n\nhttps://chart.googleapis.com/chart?chs=300x300&cht=qr&chl={}'


class BaseReactCommand(BasePostCommand):
    in_list = True
    args_template = [{
        'long': 'anon',
        'short': 'a',
        'help': 'it will be anonymous, your name will not be stored in our database',
    }]


class LikeCommand(BaseReactCommand):
    command = 'like'
    description = 'like post'

    def run(self):
        return (LikeStep, {})


class DislikeCommand(BaseReactCommand):
    command = 'dislike'
    description = 'dislike post'

    def run(self):
        return (DislikeStep, {})


class BaseReactStep(BasePostEntryStep):
    is_like = None

    def run(self, anon=False):
        react = Reaction(
            post=self.post,
            is_like=self.is_like,
            address=Address.new()
        )
        if not anon:
            react.user = self.user_id
        react.save()
        self.send_message(TEXT_PAY.format(self.text_name, react.address.address))
        self.send_message(react.address.address)


class LikeStep(BaseReactStep):
    is_like = True
    text_name = 'like'


class DislikeStep(BaseReactStep):
    is_like = False
    text_name = 'dislike'
