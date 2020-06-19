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
from ..classes.modes import DRAWMODE, FOLDER
import string
import asyncio
import types

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
        self.loop = asyncio.get_event_loop()
        self.telegram_api = TelegramApi(api_id, api_hash, self.loop)

        # curses windows
        self.main_window = None
        self.chats = None
        self.messages = None

        # for updating messages in bckg
        self.drawn_active_id = None
        self.messages_processing = False
        # self.exit = False

        self.mode = MODE.CHATS
        self.folder = FOLDER.DEFAULT

        self.init_windows()
        self.init_colors()

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

    def draw_chats(self, reset_active=False):
        chat_list = self.telegram_api.get_dialogs(False if self.folder == FOLDER.DEFAULT else True)
        if self.folder == FOLDER.DEFAULT:
            chat_list.insert(0, {'name': 'Archived chats',
                                 'id': 0,
                                 'is_user': 0,
                                 'is_group': 0,
                                 'is_channel': 0,
                                 'pinned': 0})  # This is archive folder!
        self.chats.set_chat_list(chat_list)

    def go_inside(self):
        if self.folder == FOLDER.DEFAULT and self.active_id == 0:
            self.folder = FOLDER.ARHIVED
            self.draw_chats()
            self.draw_messages()

    def go_outside(self):
        if self.folder == FOLDER.ARHIVED:
            self.folder = FOLDER.DEFAULT
            self.draw_chats()
            self.draw_messages()

    def draw_messages(self):
        if self.active_id == 0:  # checking archive folder
            self.messages.clear()
            return
        messages_list = self.telegram_api.get_messages(self.active_id)
        self.log(self.active_id)
        self.messages.set_message_list(messages_list)

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
        curses.init_pair(DRAWMODE_DEFAULT, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(DRAWMODE_SELECTED, curses.COLOR_YELLOW, curses.COLOR_BLACK)

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
    def active_id(self):
        return self.chats.active_id

    async def updates_handler(self):
        while True:
            if self.telegram_api.new_data:
                self.draw_chats()
                self.draw_messages()

            await asyncio.sleep(1)

    def keyboard_handler(self):
        while True:
            ch = self.main_window.getch()
            if ch == ord('j'):
                self.chats.move_down()
                self.draw_messages()
            if ch == ord('k'):
                self.chats.move_up()
                self.draw_messages()
            if ch == ord('l'):
                self.go_inside()
            if ch == ord('h'):
                self.go_outside()
            # if ch == ord('K'):
            #     self.messages.move_up()
            # if ch == ord('J'):
            #     self.messages.move_down()
            if ch == ord('q'):
                self.exit()
            # if ch == ord('l') and self.mode == MODE.CHATS and self.real_active_id == 0:
            #     self.change_mode(MODE.ARCHIVED)
            # if ch == ord('h') and self.mode == MODE.ARCHIVED:
            #     self.change_mode(MODE.CHATS)
            # if ch == ord('i'):
            #     # insert mode
            #     pass
            # if ch == ord('r'):
            #     # reload ui
            #     self.redraw()

    def exit(self, code=0):
        self.loop.stop()
        self.main_window.clear()
        self.main_window.refresh()
        exit(code)

    def run(self):
        # self.loop.create_task(self.draw_chats())
        self.draw_chats()
        self.draw_messages()
        self.loop.create_task(self.updates_handler())

        threading.Thread(target=self.keyboard_handler).start()

        self.loop.run_forever()

    @staticmethod
    def log(msg):
        with open('echo.txt', 'w') as f:
            f.write('\n\n\n')
            f.write(str(msg))
            f.write('\n\n\n')
