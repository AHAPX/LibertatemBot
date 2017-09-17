import logging

import config
from bot import Bot
from session import Session


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


if __name__ == '__main__':
    bot = Bot(Session())
    try:
        logger.info('service started')
        bot.run()
    except Exception as e:
        logger.critical(e)
