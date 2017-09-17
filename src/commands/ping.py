from commands.base import BaseCommand


class PingCommand(BaseCommand):
    command = 'ping'
    in_list = True
    description = 'test connection'

    def entrypoint(self, bot, update):
        self.send_message(bot, update, text='pong')
