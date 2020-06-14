import curses
from time import sleep
from ..tools.telegram import get_chats
from .chats import  Chats
from .writer import Writer
from .messages import Messages

# sizes of windows
CHATS_WIDTH = 1
MESSAGES_WIDTH = 4
WRITER_HEIGHT = 1
MESSAGES_HEIGHT = 6

# margins between windows
CHATS_MARGIN = 1
WRITER_MARGIN = 3

# number of color pair
ACTIVE_CHAT = 1
INACTIVE_CHAT = 2
ALERT = 3

# global vars:
main_window = None
chats = None
messages = None
writer = None

active_chat = None


def init_colors():
    curses.start_color()
    curses.init_pair(ACTIVE_CHAT, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(INACTIVE_CHAT, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(ALERT, curses.COLOR_BLACK, curses.COLOR_RED)


def init_windows():
    global main_window, chats, messages, writer
    main_window = curses.initscr()
    height, width = main_window.getmaxyx()

    chats_width, messages_height = get_sizes(height, width)

    chats_window = main_window.subwin(height - 1, chats_width, 1, 0)

    messages_window = main_window.subwin(messages_height, width - CHATS_MARGIN - chats_width,
                                         1, chats_width + CHATS_MARGIN)
    writer_window = main_window.subwin(height - messages_height - WRITER_MARGIN, width - 1 - chats_width,
                                       messages_height + WRITER_MARGIN, chats_width + 1)
    chats = Chats(chats_window)
    messages = Messages(messages_window)
    writer = Writer(writer_window)


def get_sizes(height, width):
    """
    :param height: screen height
    :param width: screen width
    :return: (chats_width, messages_height)
    """
    chats_width = int(width / (CHATS_WIDTH + MESSAGES_WIDTH) * CHATS_WIDTH)
    messages_height = int(height / (WRITER_HEIGHT + MESSAGES_HEIGHT) * MESSAGES_HEIGHT)
    return chats_width, messages_height


def init():
    init_windows()
    init_colors()
    # loop()
    draw_chats()

def draw_chats():
    chat_list = get_chats()
    chats.set_chat_list(chat_list)
    sleep(3)
    pass


def draw_messages():
    pass


def draw_writer():
    pass


def loop():
    ch = main_window.getch()
    while ch:
        pass