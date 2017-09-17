from coins import is_address
from helpers import get_logger
from errors import ValidationError


logger = get_logger(__name__)


class BaseValidator():
    def validate(self, value):
        try:
            return self.validator(value)
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.error(e)
            raise ValidationError

    def validator(self, value):
        raise NotImplemented


class Str(BaseValidator):
    def validator(self, value):
        return value


class Int(BaseValidator):
    def validator(self, value):
        try:
            return int(value)
        except:
            raise ValidationError('please write correct number')


class Float(BaseValidator):
    def validator(self, value):
        try:
            return float(value)
        except:
            raise ValidationError('please write correct float')


class EthAddr(BaseValidator):
    def validator(self, value):
        if not is_address(value):
            raise ValidationError('address is not valid')
        return value
