import config
import validators
from errors import CriticalError, ValidationError
from entrypoint import BaseEntrypoint
from helpers import get_args, get_logger, check_next, merge_dicts, fetch_posts
from models import Post, Address


logger = get_logger('bot')


class BaseCommand(BaseEntrypoint):
    command = ''
    description = 'base command'
    in_list = False
    args_template = []
    is_debug = False

    def load_args(self):
        self.args = []
        self.kwargs = {}
        if not self.args_template:
            return
        self.args_template.append({
            'long': 'help',
            'short': 'h',
            'help': 'print this message',
        })
        for arg in get_args(self.message.text):
            args = [a for a in self.args_template if arg in (a['long'], a['short'])]
            if args:
                self.kwargs[args[0]['long']] = True
            else:
                self.args.append(arg)

    def send_help(self):
        text = []
        for arg in self.args_template:
            text.append('[/{c}](/{c}) *{l}* or [/{c}](/{c}) *{s}* - {h}'.format(
                c=self.command,
                l=arg['long'],
                s=arg['short'],
                h=arg['help']
            ))
        self.send_message('\n\n'.join(text))

    def help_text(self):
        return '[/{c}](/{c})\t-\t{d}'.format(c=self.command, d=self.description)

    def entrypoint(self, bot, update):
        super(BaseCommand, self).entrypoint(bot, update)
        try:
            self.load_args()
            if 'help' in self.kwargs:
                self.send_help()
                return
            result = self.run()
            self.check_next(result)
        except Exception as e:
            logger.error(e)


class BasePostCommand(BaseCommand):
    owner_only = False

    def entrypoint(self, bot, update):
        self.load(bot, update)
        try:
            Post.get(Post.id == self.get_session('post_id'))
            next_point = self.run()
            if check_next(next_point):
                self.set_session(**next_point[1])
                return next_point[0](self.session).entrypoint(bot, update)
            self.send_message('system error')
        except:
            posts = self.print_posts()
            if posts:
                self.set_session(posts=posts)
            super(BasePostCommand, self).entrypoint(bot, update)

    def print_posts(self):
        select = Post.select().join(Address).\
            where(
                Address.is_accepted == True,
                Post.is_deleted == False
            ).\
            order_by(Post.created_at.desc()).\
            limit(config.POSTS_LIMIT)
        if self.owner_only:
            select = select.where(Post.user == self.user_id)
        posts, text, keyboards = fetch_posts(select)
        if len(posts) < 1:
            self.send_message('posts not found')
            return
        self.send_message(
            '{}\n\n *select number of post*?'.format('\n\n'.join(text)),
            keyboards=keyboards
        )
        return posts


class BaseDocCommand(BaseCommand):
    doc_file = ''

    def run(self):
        if self.doc_file:
            self.send_message(open(self.doc_file).read(), preview=False)


class BaseStep(BaseEntrypoint):
    validator = None
    valid_name = ''

    def __init__(self, session):
        super(BaseStep, self).__init__(session)
        self.data = None

    def validate(self):
        next_point = self.get_session('next')
        if not check_next(next_point) or not isinstance(self, next_point[0]):
            raise CriticalError
        if self.validator and issubclass(self.validator, validators.BaseValidator):
            self.data = self.validator().validate(self.message.text)
        if self.valid_name and self.data is not None:
            return merge_dicts(next_point[1], {self.valid_name: self.data})
        return next_point[1]

    def entrypoint(self, bot, update):
        super(BaseStep, self).entrypoint(bot, update)
        try:
            params = self.validate()
        except ValidationError as e:
            self.send_message(e.message)
            return (type(self), self.get_session('next')[1])
        try:
            result = self.run(**params)
            if check_next(result):
                return result
        except Exception as e:
            logger.error(e)

    @classmethod
    def get(cls, obj):
        instance = cls(obj.session)
        instance.bot = obj.bot
        instance.message = obj.message
        instance.user_id = obj.user_id
        instance.post = obj.post
        return instance


class BasePostStep(BaseStep):
    def entrypoint(self, bot, update):
        self.load(bot, update)
        try:
            self.post = Post.get(Post.id == self.get_session('post_id'))
        except Post.DoesNotExist:
            self.send_message('post not found')
        else:
            return super(BasePostStep, self).entrypoint(bot, update)


class BasePostEntryStep(BasePostStep):
    validator = validators.Int
    valid_name = 'num'

    def entrypoint(self, bot, update):
        self.load(bot, update)
        try:
            self.post = Post.get(Post.id == self.get_session('post_id'))
        except:
            try:
                posts = self.get_session('posts')
                params = self.validate()
                self.post = Post.get(Post.id == posts[params['num'] - 1])
                self.set_session(post_id=self.post.id)
            except ValidationError as e:
                self.send_message(e.message)
                return (type(self), self.get_session('next')[1])
            except:
                self.send_message('post not found')
                return
        try:
            result = self.run()
            self.check_next(result)
        except Exception as e:
            logger.error(e)
