import copy
import hashlib
import logging
import random

import telegram

import config


def get_logger(name):
    logger = logging.getLogger(name or 'libertatem')
    logger.setLevel(logging.INFO)
    return logger


def get_bot():
    return telegram.Bot(config.TOKEN)


def gen_token(text='', size=8):
    if text:
        text = text.encode()
    else:
        text = str(random.random()).encode()
    return hashlib.md5(text).hexdigest()[:size]


def get_args(text):
    try:
        return text.split(' ')[1:]
    except:
        return []


def text_cut(text):
    if len(text) <= config.TEXT_CUT_MAX:
        return text
    return '{}...'.format(text[:config.TEXT_CUT_MIN])


def send_message(bot, user_id, text, keyboards=None, preview=True):
    if isinstance(keyboards, list) and keyboards:
        markup = telegram.ReplyKeyboardMarkup(keyboards)
    else:
        markup = telegram.ReplyKeyboardRemove()
    return bot.send_message(
        chat_id=user_id,
        text=text,
        parse_mode='Markdown',
        reply_markup=markup,
        disable_web_page_preview=not preview
    )


def keyboard_split(keyboard, max_line=4):
    result = []
    keys = []
    for key in keyboard:
        if len(keys) >= max_line:
            result.append(keys)
            keys = []
        keys.append(key)
    if keys:
        result.append(keys)
    return result


def fetch_posts(select):
    text = []
    keyboard = []
    posts = []
    counter = 1
    for post in select:
        text.append('*number: {}*\n*balance {}*\n`{}`'.format(counter, post.get_full_balance(), text_cut(post.text)))
        posts.append(post.id)
        keyboard.append(str(counter))
        counter += 1
    return posts, text, keyboard_split(keyboard)


def post_message(post, balance, bot=None):
    bot = bot or get_bot()
    if post.forward_chat_id and post.forward_message_id:
        message = bot.forward_message(
            chat_id=config.CHANNEL_NAME,
            from_chat_id=post.forward_chat_id,
            message_id=post.forward_message_id
        )
    else:
        message = bot.send_message(config.CHANNEL_NAME, text=post.text, parse_mode='Markdown')
    post.balance = balance
    post.message_id = message.message_id
    post.save()
    if post.user:
        send_message(bot, int(post.user), text='your message was posted')


def add_react(react, amount, bot=None):
    bot = bot or get_bot()
    name = 'like' if react.is_like else 'dislike'
    react.amount = amount
    react.save()
    if react.is_like:
        react.post.balance += amount
    else:
        react.post.balance -= amount
    if react.post.balance <= 0:
        react.post.is_deleted = True
    react.post.save()
    if react.user:
        send_message(bot, int(react.user), text='your {} accepted'.format(name))
    if react.post.user:
        send_message(bot, int(react.post.user), text='your post received {} for {}ETH'.format(name, react.amount))
# TODO: what if delete return error, but db already changed
    if react.post.balance <= 0:
        bot.delete_message(chat_id=config.CHANNEL_NAME, message_id=react.post.message_id)
        if react.post.user:
            send_message(bot, int(react.post.user), text='your post was deleted')


def check_next(data):
    from commands.base import BaseStep

    if not data or not isinstance(data, (list, tuple)) or len(data) != 2:
        return False
    if not issubclass(data[0], BaseStep) or not isinstance(data[1], dict):
        return False
    return True


def merge_dicts(d1, d2):
    result = copy.copy(d1)
    result.update(d2)
    return result
