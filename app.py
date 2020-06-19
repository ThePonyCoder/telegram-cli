import curses
from time import sleep
import sys
from teletools.core.core import Core

sys.stdout = open('stdout.txt','w')

with open('auth.txt','r') as f:
    api_id = f.readline().strip()
    api_hash = f.readline().strip()

    core = Core(api_id, api_hash)

    core.run()





