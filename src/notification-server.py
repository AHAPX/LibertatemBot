import json
import logging
from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer

import config
from helpers import post_message, add_react
from models import Address


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            handle(json.loads(post_data.decode()))
        except Exception as e:
            logger.error(e)
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()


def handle(data):
    if data.get('type') != 'wallet:addresses:new-payment':
        return
    address = data.get('data', {}).get('address')
    amount = float(data.get('additional_data', {}).get('amount', {}).get('amount'))
    if not address or amount:
        logger.error('address = {}, amount = {}'.format(address, amount))
    try:
        addr = Address.get(Address.address == address)
    except Address.DoesNotExist:
        logger.warning('{} not found'.format(address))
        return
    with config.DB.atomic() as tnx:
        try:
            if amount != addr.balance:
                if addr.post.count():
                    post_message(addr.post[0], amount)
                elif addr.reaction.count():
                    add_react(addr.reaction[0], amount)
                addr.is_accepted = True
                logger.info('addr = {} ({}) accepted'.format(addr.address, addr.id))
            addr.balance += amount
            addr.save()
            tnx.commit()
        except Exception as e:
            logger.error(e)
            tnx.rollback()


def run():
    httpd = TCPServer((config.NOTIFY_ADDR, config.NOTIFY_PORT), Handler)
    logger.info('Server started...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
