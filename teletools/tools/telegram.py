from random import random

from ..classes.chat import Chat


def auth():
    pass


def get_chats():
    chat_list = ['zsdasd', 'xcxcxc', 'zzzzz']
    ret = []
    for i in chat_list:
        ret.append(Chat(random(), i))

    return ret


def get_messages():
    pass
