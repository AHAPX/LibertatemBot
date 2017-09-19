from datetime import timedelta

DEBUG = False

MAX_TIME_GAP = timedelta(seconds=5)
POSTS_LIMIT = 10
TEXT_CUT_MIN = 100
TEXT_CUT_MAX = 130
MIN_AMOUNT = 0.001
COMMANDS_IN_LINE = 5
MESSAGE_TYPES = ['photo', 'sticker', 'audio', 'voice', 'video']

### MUST BE SET UP IN local.py
# telegram settions
CHANNEL_NAME = '@CHANNEL'
CHANNEL_ID = 0
TOKEN = 'TOKEN'
ADMIN_ID = 0
ADMIN_DEFAULT_BALANCE = 10

# coinbase settings
WALLET_API_KEY = 'coinbase_apikey'
WALLET_API_SECRET = 'coinbase_apisecret'
WALLET_TYPE = 'ETH'

# notifition server settings
NOTIFY_ADDR = '0.0.0.0'
NOTIFY_PORT = 9457

from peewee import SqliteDatabase
DB = SqliteDatabase('test.db')

try:
    from local import *
except Exception as e:
    print(e)
