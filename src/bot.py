from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import config
from commands import commands, base
from entrypoint import BaseEntrypoint
from helpers import text_cut, keyboard_split, get_logger, check_next
from models import Post


logger = get_logger(__name__)


def error_callback(bot, update, error):
    raise error


class Bot(BaseEntrypoint):
    list_commands = []
    post_commands = []

    def is_post(self):
        post = None
        if self.message.forward_from_chat and str(self.message.forward_from_chat.id) == str(config.CHANNEL_ID):
            try:
                post = Post.get(Post.message_id == self.message.forward_from_message_id)
            except Exception as e:
                logger.error(e)
#        elif self.message.forward_date:
#            try:
#                post = Post.join(Address).get(
#                    Post.text == self.message.text,
#                    self.message.forward_date - Post.created_at < config.MAX_TIME_GAP,
#                    Post.is_deleted == False,
#                    Address.is_accepted == True
#                )
#            except Exception as e:
#                logger.error(e)
        if post:
            self.reset_session()
            self.set_session(post_id=post.id)
            text = '*balance: {}*\n`{}`\n\n*what would you like to do with this post?*'.format(
                post.get_full_balance(),
                text_cut(post.content.text)
            )
            keyboards = []
            for com in self.post_commands:
                if not com.owner_only or str(post.user) == str(self.user_id):
                    keyboards.append('/{}'.format(com.command))
            self.send_message(text=text, keyboards=keyboard_split(keyboards))
            return True
        return False

    def entirypoint(self, bot, update):
        super(Bot, self).entrypoint(bot, update)
        if self.is_post():
            return
        next_point = self.get_session('next')
        if check_next(next_point):
            try:
                result = next_point[0](self.session).entrypoint(bot, update)
                self.check_next(result)
            except Exception as e:
                logger.error(e)
        else:
            self.reset_session()
            helps = []
            keyboards = []
            for com in self.list_commands:
                helps.append(com.help_text())
                keyboards.append('/{}'.format(com.command))
            text = '*Commands*\n{}'.format('\n'.join(helps))
            self.send_message(text, keyboards=keyboard_split(keyboards, config.COMMANDS_IN_LINE))

    def run(self):
        updater = Updater(config.TOKEN)
        updater.dispatcher.add_handler(MessageHandler(Filters.text, self.entirypoint))
        for t in config.MESSAGE_TYPES:
            filt = getattr(Filters, t, None)
            if filt:
                updater.dispatcher.add_handler(MessageHandler(filt, self.entirypoint))
        updater.dispatcher.add_error_handler(error_callback)
        self.list_commands = []
        self.post_commands = []
        for command in commands:
            if command.is_debug and not config.DEBUG:
                continue
            com = command(self.session)
            updater.dispatcher.add_handler(CommandHandler(com.command, com.entrypoint))
            if com.in_list:
                self.list_commands.append(com)
            if isinstance(com, base.BasePostCommand):
                self.post_commands.append(com)
        updater.start_polling()
        updater.idle()
