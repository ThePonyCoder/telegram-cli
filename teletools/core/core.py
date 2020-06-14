import curses
import  curses.textpad
from time import sleep
from ..tools.telegram import TelegramApi
from .chats import Chats
from .writer import Writer
from .messages import Messages
import string

# sizes of windows
CHATS_WIDTH = 2
MESSAGES_WIDTH = 3
WRITER_HEIGHT = 1
MESSAGES_HEIGHT = 6

# margins between windows
CHATS_MARGIN = 1
WRITER_MARGIN = 3

# number of color pair
COLORS = {}

# global vars:
main_window = None
chats = None
messages = None
writer = None

active_chat = None

telegram_api = None


def init_colors():
    global COLORS
    ACTIVE_CHAT = 1
    INACTIVE_CHAT = 2
    ALERT = 3
    AUTHOR = 4

    curses.start_color()
    curses.init_pair(ACTIVE_CHAT, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(INACTIVE_CHAT, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(ALERT, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(AUTHOR, curses.COLOR_GREEN, curses.COLOR_BLACK)

    COLORS = {
        'active': curses.color_pair(ACTIVE_CHAT),
        'inactive': curses.color_pair(INACTIVE_CHAT),
        'alert': curses.color_pair(ALERT),
        'author': curses.color_pair(AUTHOR)
    }
    print(COLORS)

    chats.init_colors(COLORS)
    messages.init_colors(COLORS)


def init_windows():
    global main_window, chats, messages, writer
    main_window = curses.initscr()
    curses.noecho()
    curses.curs_set(0)
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


def init_api(api_id, api_hash):
    global telegram_api
    telegram_api = TelegramApi(api_id, api_hash)


def init(api_id, api_hash):
    init_api(api_id, api_hash)
    init_windows()
    init_colors()

    draw_chats()
    draw_messages()



    loop()






def draw_chats():
    chat_list = telegram_api.get_chats()
    chats.set_chat_list(chat_list)


def reload_active_chat():
    pass


def draw_messages():
    messages_list = telegram_api.get_messages(chats.active_id)
    messages.set_message_list(messages_list)


def draw_writer():
    pass


def loop():
    ch = main_window.getch()
    while ch:
        if ch == ord('j'):
            chats.move_down()
            draw_messages()
        if ch == ord('k'):
            chats.move_up()
            draw_messages()
        if ch == ord('K'):
            messages.move_up()
        if ch == ord('J'):
            messages.move_down()
        if ch == ord('q'):
            main_window.clear()
            main_window.refresh()
            exit(0)
        if ch == ord('i'):
            # insert mode
            pass
        if ch == ord('r'):
            # reload ui
            pass


        ch = main_window.getch()
