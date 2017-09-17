from commands.base import BaseCommand, BaseDocCommand


class StartCommand(BaseCommand):
    command = 'start'
    description = 'welcome message'
    in_list = True

    def run(self):
        self.send_message('Welcome to Libertatem project!\nRead info http://telegra.ph/libertatemx-09-10')


class PingCommand(BaseCommand):
    command = 'ping'
    description = 'test connection'
    in_list = True

    def run(self):
        self.send_message('pong')


class AboutCommand(BaseDocCommand):
    command = 'about'
    description = 'about project'
    in_list = True
    doc_file = 'docs/about.md'


class InfoCommand(BaseDocCommand):
    command = 'info'
    description = 'detail info about project'
    in_list = True
    doc_file = 'docs/info.md'


class CancelCommand(BaseCommand):
    command = 'cancel'
    description = 'cancel last action'

    def run(self):
        self.send_message('cancelled')

