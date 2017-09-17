class BaseError(Exception):
    message = 'base custom error'

    def __init__(self, message):
        if message:
            self.message = message


class CriticalError(BaseException):
    message = 'critical error'


class ValidationError(BaseError):
    message = 'validation error'
