import copy
import hashlib
import logging
import random

import telegram

import config
import consts
from errors import ContentError


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
        text.append('*number: {}*\n*balance {}*\n`{}`'.format(
            counter,
            post.get_full_balance(),
            text_cut(post.content.text)
        ))
        posts.append(post.id)
        keyboard.append(str(counter))
        counter += 1
    return posts, text, keyboard_split(keyboard)


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


def get_content(message):
    cont_type = consts.CONTENT_TEXT
    text = message.text
    file_id = None
    if message.photo:
        file_id = message.photo[0].file_id
        cont_type = consts.CONTENT_PHOTO
    elif message.audio:
        file_id = message.audio.file_id
        cont_type = consts.CONTENT_AUDIO
    elif message.voice:
        file_id = message.voice.file_id
        cont_type = consts.CONTENT_VOICE
    elif message.video:
        file_id = message.video.file_id
        cont_type = consts.CONTENT_VIDEO
    elif message.sticker:
        file_id = message.sticker.file_id
        cont_type = consts.CONTENT_STICKER
    if not (text or file_id):
        raise ContentError
    return cont_type, text, file_id
