import config
import validators
from coins import send_coins
from commands.base import BasePostCommand, BasePostStep, BasePostEntryStep


shares = [1, 0.5, 0.25, 0.1]


class WithdrawCommand(BasePostCommand):
    command = 'withdraw'
    description = 'withdraw ethereum from post\'s balance'
    in_list = True
    owner_only = True

    def run(self):
        return (AddressStep, {})


class AddressStep(BasePostEntryStep):
    def run(self):
        self.send_message('please write your ethereum wallet address')
        return (AmountStep, {})


class AmountStep(BasePostStep):
    validator = validators.EthAddr
    valid_name = 'address'

    def run(self, address):
        keyboard = []
        for share in shares:
            value = share * self.post.balance
            if value >= config.MIN_AMOUNT:
                keyboard.append(str(value))
        self.send_message(
            'balance of post = {}\n\n*how much you would like to withdraw?*'.format(self.post.balance),
            keyboards=[keyboard]
        )
        return (WithdrawStep, {'address': address})


class WithdrawStep(BasePostStep):
    validator = validators.Float
    valid_name = 'amount'

    def run(self, amount, address):
        if amount < config.MIN_AMOUNT:
            self.send_message('amount cannot be less than {}'.format(config.MIN_AMOUNT))
            return AmountStep.get(self).run(address)
        if amount > self.post.balance:
            self.send_message('amount is bigger than balance, try to withdraw less amount')
            return AmountStep.get(self).run(address)
        if send_coins(address, amount):
# TODO: what if db returns error, when coins already left
            self.send_message('{} eth sent to {}'.format(amount, address))
            self.post.balance -= amount
            if self.post.balance <= 0:
                self.post.is_deleted = True
                self.bot.delete_message(chat_id=config.CHANNEL_NAME, message_id=self.post.message_id)
                if self.post.user:
                    self.send_message('your post was deleted', user_id=int(self.post.user))
            self.post.save()
        else:
            self.send_message('something went wrong, try again')
