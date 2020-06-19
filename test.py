import curses
from pprint import pprint
from time import sleep

from teletools.tools.telegram import TelegramApi

with open('auth.txt', 'r') as f:
    api_id = f.readline().strip()
    api_hash = f.readline().strip()

    TelegramApi(api_id, api_hash)



with open('debug.txt','w') as f:
    f.write()
    f.write('\n')