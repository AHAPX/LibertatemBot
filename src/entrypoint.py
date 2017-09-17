from helpers import send_message, check_next


class BaseEntrypoint():
    session = None

    def __init__(self, session):
        self.session = session

    def get_session(self, param=None):
        return self.session.get(self.user_id, param=param)

    def set_session(self, **kwargs):
        self.session.set(self.user_id, **kwargs)

    def reset_session(self, **kwargs):
        self.session.reset(self.user_id)

    def send_message(self, text, keyboards=None, preview=True, user_id=None):
        user_id = user_id or self.user_id
        return send_message(self.bot, user_id, text, keyboards, preview=preview)

    def load(self, bot, update):
        self.bot = bot
        self.message = update.message
        self.user_id = update.message.from_user.id

    def entrypoint(self, bot, update):
        self.load(bot, update)

    def check_next(self, data):
        if check_next(data):
            self.set_session(next=data)
        else:
            self.reset_session()

    def run(self, *args, **kwargs):
        raise NotImplemented

