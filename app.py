import curses
from time import sleep

from teletools.core.core import Core

with open('auth.txt','r') as f:
    api_id = f.readline().strip()
    api_hash = f.readline().strip()

    core = Core(api_id, api_hash)

    core.loop()





