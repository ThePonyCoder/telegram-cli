import curses
from time import sleep

import teletools.core.core

with open('auth.txt','r') as f:
    api_id = f.readline().strip()
    api_hash = f.readline().strip()

    teletools.core.core.init(api_id, api_hash)





