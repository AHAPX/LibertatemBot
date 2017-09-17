import validators
from coins import is_address
from commands.base import BaseCommand, BaseStep
from models import Settings


TEXT_ADDRESS = 'your current address - *{}*\n send new one if you want to change or [/cancel](/cancel)'


class SettingsCommand(BaseCommand):
    command = 'settings'
    description = 'user settings'
    in_list = True

    def run(self):
        keyboards = [('wallet',)]
        self.send_message('choose settings to change', keyboards=keyboards)
        return (Step1, {})


class BaseOptionStep(BaseStep):
    def get_settings(self):
        try:
            return Settings.get(Settings.user == self.user_id)
        except Settings.DoesNotExist:
            return Settings.create(user=self.user_id)


class Step1(BaseOptionStep):
    validator = validators.Str
    valid_name = 'option'

    def run(self, option):
        if option == 'wallet':
            settings = self.get_settings()
            if settings.address:
                self.send_message(TEXT_ADDRESS.format(settings.address))
            else:
                self.send_message('send your ethereum wallet address')
            return (WalletStep, {})
        self.send_message('setting now found')


class WalletStep(BaseOptionStep):
    validator = validators.EthAddr
    valid_name = 'address'

    def run(self, address):
        if not is_address(address):
            self.send_message('address is not valid')
            return (self, {})
        settings = self.get_settings()
        settings.address = address
        settings.save()
        self.send_message('address saved')
