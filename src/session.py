class Session():
    users = {}

    def get(self, user_id, param=None):
        user = self.users.get(user_id, {})
        if param:
            return user.get(param)
        return user

    def set(self, user_id, **kwargs):
        self.users[user_id] = self.users.get(user_id, {})
        self.users[user_id].update(kwargs)

    def set_param(self, user_id, param, value):
        self.users.get(user_id, {})[param] = value

    def reset(self, user_id):
        self.users[user_id] = {}
