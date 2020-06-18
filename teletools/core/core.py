import curses
import curses.textpad
import threading
from random import random
from time import sleep
from ..tools.telegram import TelegramApi
from .chats import Chats
from .writer import Writer
from .messages import Messages
from ..classes.modes import MODE
from ..classes.chat import Chat
from ..classes.modes import DRAWMODE
import string

# sizes of windows
CHATS_WIDTH = 2
MESSAGES_WIDTH = 3
WRITER_HEIGHT = 1
MESSAGES_HEIGHT = 6

# margins between windows
CHATS_MARGIN = 1
WRITER_MARGIN = 3


class Core:
    def __init__(self, api_id, api_hash):
        self.telegram_api = TelegramApi(api_id, api_hash)

        # curses windows
        self.main_window = None
        self.chats = None
        self.messages = None

        # for updating messages in bckg
        self.drawn_active_id = None
        self.messages_processing = False
        self.exit = False

        self.mode = MODE.CHATS

        self.init_windows()
        self.init_colors()

        self.draw_chats()
        # self.draw_messages()

    def init_windows(self):
        self.main_window = curses.initscr()
        self.main_window.clear()
        self.main_window.refresh()
        curses.noecho()
        curses.curs_set(0)
        height, width = self.main_window.getmaxyx()

        chats_width, messages_height = self.get_sizes(height, width)

        chats_window = self.main_window.subwin(height - 1, chats_width, 1, 0)

        messages_window = self.main_window.subwin(messages_height, width - CHATS_MARGIN - chats_width,
                                                  1, chats_width + CHATS_MARGIN)
        writer_window = self.main_window.subwin(height - messages_height - WRITER_MARGIN, width - 1 - chats_width,
                                                messages_height + WRITER_MARGIN, chats_width + 1)
        self.chats = Chats(chats_window)
        self.messages = Messages(messages_window)

    def draw_chats(self, reactive=False):

        chat_list = self.telegram_api.get_dialogs()
        if self.mode == MODE.CHATS:
            chat_list = [i for i in chat_list if i.archived is False]
            chat_list.insert(0, Chat(chat=None))  # This is archive folder!
            self.chats.set_chat_list(chat_list, reactive=reactive)
        if self.mode == MODE.ARCHIVED:
            chat_list = [i for i in chat_list if i.archived is True]
            self.chats.set_chat_list(chat_list, reactive=reactive)

    def change_mode(self, mode):
        if mode == MODE.ARCHIVED:
            self.mode = MODE.ARCHIVED
            self.draw_chats(reactive=True)
        if mode == MODE.CHATS:
            self.mode = MODE.CHATS
            self.draw_chats(reactive=True)

    def draw_messages_thread(self):
        while True:
            if self.real_active_id != self.drawn_active_id:
                self.messages_processing = True
                self.drawn_active_id = self.real_active_id
                if self.real_active_id:  # check if we selected archive folder!
                    messages_list = self.telegram_api.get_messages(self.real_active_id)
                    self.messages.set_message_list(messages_list)
                else:
                    self.messages.clear()
                self.messages_processing = False
            if self.exit:
                break
            sleep(0.2)

    def wait_message_draw(self):
        self.drawn_active_id = self.real_active_id

    def redraw(self):
        self.main_window.clear()
        self.main_window.refresh()
        self.init_windows()
        self.init_colors()

        self.draw_chats()

    def init_colors(self):
        ACTIVE_CHAT = 1
        INACTIVE_CHAT = 2
        ALERT = 3
        AUTHOR = 4

        DRAWMODE_DEFAULT = 5
        DRAWMODE_SELECTED = 6

        curses.start_color()
        curses.init_pair(ACTIVE_CHAT, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(INACTIVE_CHAT, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(ALERT, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(AUTHOR, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(DRAWMODE_DEFAULT, curses.COLOR_WHITE,curses.COLOR_BLACK)
        curses.init_pair(DRAWMODE_SELECTED, curses.COLOR_YELLOW,curses.COLOR_BLACK)

        COLORS = {
            'active': curses.color_pair(ACTIVE_CHAT),
            'inactive': curses.color_pair(INACTIVE_CHAT),
            'alert': curses.color_pair(ALERT),
            'author': curses.color_pair(AUTHOR),
            DRAWMODE.DEFAULT: curses.color_pair(DRAWMODE_DEFAULT),
            DRAWMODE.SELECTED: curses.color_pair(DRAWMODE_SELECTED)
        }

        self.chats.init_colors(COLORS)
        self.messages.init_colors(COLORS)

    @staticmethod
    def get_sizes(height, width):
        """
        :param height: screen height
        :param width: screen width
        :return: (chats_width, messages_height)
        """
        chats_width = int(width / (CHATS_WIDTH + MESSAGES_WIDTH) * CHATS_WIDTH)
        messages_height = int(height / (WRITER_HEIGHT + MESSAGES_HEIGHT) * MESSAGES_HEIGHT)
        return chats_width, messages_height

    @property
    def real_active_id(self):
        return self.chats.active_id

    def loop(self):
        # starting draw_messages_thread()
        # threading.Thread(target=self.draw_messages_thread).start()

        ch = self.main_window.getch()
        while ch:
            if ch == ord('j'):
                self.chats.move_down()
                # self.draw_messages()
            if ch == ord('k'):
                self.chats.move_up()
                # self.draw_messages()
            if ch == ord('K'):
                self.messages.move_up()
            if ch == ord('J'):
                self.messages.move_down()
            if ch == ord('q'):
                self.main_window.clear()
                self.main_window.refresh()
                self.exit = True
                exit(0)
            if ch == ord('l') and self.mode == MODE.CHATS and self.real_active_id == 0:
                self.change_mode(MODE.ARCHIVED)
            if ch == ord('h') and self.mode == MODE.ARCHIVED:
                self.change_mode(MODE.CHATS)
            if ch == ord('i'):
                # insert mode
                pass
            if ch == ord('r'):
                # reload ui
                self.redraw()

            ch = self.main_window.getch()

    @staticmethod
    def log(msg):
        with open('echo.txt', 'r+') as f:
            f.write('\n\n\n')
            f.write(str(msg))
            f.write('\n\n\n')
