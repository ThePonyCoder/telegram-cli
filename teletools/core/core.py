import curses
import curses.textpad
import threading
from random import random
import time
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
from ..tools.database import Database

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
        # self.loop = asyncio.get_event_loop()
        # self.telegram_api = TelegramApi(api_id, api_hash, self.loop)
        self.database = Database()

        # curses windows
        self.main_window = None
        self.chats = None
        self.messages = None

        # for updating messages in bckg
        # self.drawn_active_id = None
        # self.messages_processing = False
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

        chats_window = self.main_window.subwin(height - 2, chats_width, 1, 0)

        messages_window = self.main_window.subwin(messages_height, width - CHATS_MARGIN - chats_width - 1,
                                                  1, chats_width + CHATS_MARGIN)
        writer_window = self.main_window.subwin(height - messages_height - WRITER_MARGIN - 1, width - 1 - chats_width,
                                                messages_height + WRITER_MARGIN, chats_width + 1)
        self.chats = Chats(chats_window)
        self.messages = Messages(messages_window)

    def draw_chats(self, reset_active=False):
        # chat_list = self.telegram_api.get_dialogs(False if self.folder == FOLDER.DEFAULT else True)
        self.update_dialogs()
        chat_list = self.database.get_dialogs()

        def _get_chat_flags(chat):
            """Make flags for chat"""
            status = ''
            status += 'p' if chat['pinned'] else '-'
            if chat['is_user']:
                status += 'u'
            elif chat['is_channel']:
                status += 'c'
            elif chat['is_group']:
                status += 'g'
            else:
                status += '-'
            return status

        reduced_chat_list = [{
            'name': i['name'],
            'id': i['id'],
            'flags': _get_chat_flags(i)
        } for i in chat_list]

        if self.folder == FOLDER.DEFAULT:
            reduced_chat_list.insert(0, {'name': 'Archived chats',
                                         'id': 0,
                                         'flags': '-f'
                                         })  # This is archive folder!
        self.chats.set_chat_list(reduced_chat_list)

    def go_inside(self):
        pass
        if self.folder == FOLDER.DEFAULT and self.chats.get_active_chat_id() == 0:
            self.folder = FOLDER.ARHIVED
            self.draw_chats()
            self.draw_messages()

    def go_outside(self):
        pass
        if self.folder == FOLDER.ARHIVED:
            self.folder = FOLDER.DEFAULT
            self.draw_chats()
            self.draw_messages()

    def draw_messages(self):
        if self.chats.get_active_chat_id() == 0:  # checking archive folder
            self.messages.clear()
            return
        messages_list = self.database.get_messages(self.chats.get_active_chat_id())

        def _get_flags(msg):
            flags = ''
            flags += 'p' if msg.get('photo') else '-'
            flags += 'a' if msg.get('audio') else '-'
            flags += 'v' if msg.get('video') else '-'
            flags += 'V' if msg.get('voice') else '-'
            flags += 'f' if msg.get('file') else '-'
            flags += 'g' if msg.get('gif') else '-'
            flags += 's' if msg.get('sticker') else '-'
            return flags

        reduced_message_list = [{
            'title': str(self.database.get_user_name(i['from_id'])[1]),
            'id': i['id'],
            'flags': _get_flags(i),
            'text': i['message'],
            'date': i['date'],
            'media': i['media']
        } for i in messages_list]
        self.messages.set_message_list(reduced_message_list)

    def redraw(self):
        # TODO better redraw without deleting old objects
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

        self.chats.set_colors(COLORS)
        self.messages.set_colors(COLORS)

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

    def loop(self):
        while True:
            ch = self.main_window.getkey()
            if ch == 'j':
                self.chats.move_down()
                self.draw_messages()
            if ch == 'k':
                self.chats.move_up()
                self.draw_messages()
            # if ch == ord('l'):
            #     self.go_inside()
            # if ch == ord('h'):
            # self.go_outside()
            if ch == 'q':
                self.exit()
            # if ch == ord('i'):
            #     # insert mode
            #     pass
            if ch == 'r':
                self.redraw()
            # time.sleep(0.2)

    def exit(self, code=0):
        self.main_window.clear()
        self.main_window.refresh()
        exit(code)

    def run(self):
        self.draw_chats()
        self.draw_messages()

        self.loop()

    @staticmethod
    def log(msg):
        print(msg)

    def update_dialogs(self):
        pass
