from coinbase.wallet.client import Client
from web3 import Web3

import config
from helpers import get_logger


logger = get_logger(__name__)


def get_network():
    return Client(config.WALLET_API_KEY, config.WALLET_API_SECRET)


def get_account():
    return get_network().get_account(config.WALLET_TYPE)


def gen_wallet():
    return get_account().create_address()


def get_balance(addr):
    try:
        txs = get_account().get_address_transactions(addr.addr_id)
        result = sum([float(txs[i].amount.amount) for i in range(len(txs))])
    except Exception as e:
        logger.warning(e)
        result = 0
    return result


def send_coins(address, amount):
    if config.DEBUG:
        return True
    try:
        acc = get_account()
        acc.send_money(to=address, amount=amount, currency=config.WALLET_TYPE)
    except Exception as e:
        logger.error(e)
        return False
    return True


def is_address(addr):
    return Web3.isAddress(addr)
