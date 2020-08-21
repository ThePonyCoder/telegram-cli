import curses
from time import sleep
import sys
from teletools.core.core import Core
import threading
import queue

sys.stdout = open('stdout.txt', 'w', buffering=1)

with open('auth.txt', 'r') as f:
    api_id = f.readline().strip()
    api_hash = f.readline().strip()

    new_data_event = threading.Event()
    update_queue = queue.Queue()
    core = Core(new_data_event=new_data_event, update_queue=update_queue)

    core.run()
