import string
import curses
import curses.textpad
import queue
import threading
import time
import os

from .chats import Chats
from .messages import Messages
from ..classes.modes import DRAWMODE, FOLDER
from ..classes.modes import MODE, Colors
from ..tools.database import Database
from ..classes.update import Update, UpdateType
from .statusline import Status

# sizes of windows
CHATS_WIDTH = 2
MESSAGES_WIDTH = 3
WRITER_HEIGHT = 1
MESSAGES_HEIGHT = 6

# margins between windows
CHATS_MARGIN = 1
WRITER_MARGIN = 3


class Core:
    def __init__(self, new_data_event: threading.Event, update_queue: queue.Queue):
        self.database = Database()

        # curses windows
        self.main_window = None
        self.chats = None
        self.messages = None
        self.status = None

        self.mode = MODE.CHATS
        self.folder = FOLDER.DEFAULT

        # synchronisation between threads
        self.new_data_event = new_data_event
        self.update_queue = update_queue

        # many actions at a time
        self.char_query = ''

        self.init_windows()

        threading.Thread(target=self.continuous_updates).start()

    def continuous_updates(self):
        while True:
            self.main_window.refresh()
            if self.new_data_event.is_set():
                self.draw_chats(noupdate=True)
                self.draw_messages(noupdate=True)
                self.new_data_event.clear()
            time.sleep(1)

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
        status_window = self.main_window.subwin(1, width, height - 1, 0)

        self.chats = Chats(chats_window)
        self.messages = Messages(messages_window)
        self.status = Status(status_window)

    def draw_chats(self, noupdate=False):
        if not noupdate:
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
        if self.folder == FOLDER.DEFAULT and self.__get_active_id() == 0:
            self.folder = FOLDER.ARHIVED
            self.draw_chats()
            self.draw_messages()

    def go_outside(self):
        pass
        if self.folder == FOLDER.ARHIVED:
            self.folder = FOLDER.DEFAULT
            self.draw_chats()
            self.draw_messages()

    def __get_active_id(self):
        return self.chats.get_active_chat_id()

    def draw_messages(self, noupdate=False):
        if self.__get_active_id() == 0:  # checking archive folder
            self.messages.clear()
            return
        if not noupdate:
            self.update_messages(self.__get_active_id())
        messages_list = self.database.get_messages(self.__get_active_id())

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
        active_chat_id = self.__get_active_id()
        self.main_window.clear()
        self.main_window.refresh()
        self.init_windows()

        self.draw_chats()
        self.chats.set_active_chat_id(active_chat_id)
        self.draw_messages()

        # self.chats.set_colors(COLORS)
        # self.messages.set_colors(COLORS)
        # self.status.set_colors(COLORS)

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

    def key_handler(self, key):
        if key in string.digits:
            self.update_query(key)

        if key == 'j':
            self.chats.move_down(int(self.char_query) if self.char_query else 1)
            self.draw_messages()
        if key == 'k':
            self.chats.move_up(int(self.char_query) if self.char_query else 1)
            self.draw_messages()

        if key == 'q':
            self.exit()
            return

        if key == 'o' and self.char_query != '':
            self.download_media(self.__get_active_id(), int(self.char_query))

        if key == 'R' or key == 'KEY_RESIZE':
            self.redraw()

        if key not in string.digits:
            self.update_query()

    def update_query(self, char=None):
        if char is None:
            self.char_query = ''
        else:
            self.char_query += char
        self.status.set_char_query(self.char_query)

    def loop(self):
        while True:
            ch = self.main_window.getkey()
            print(ch)
            self.key_handler(ch)

    def exit(self, code=0):
        curses.endwin()
        os._exit(0)

    def run(self):
        self.draw_chats()
        self.draw_messages()
        self.status._update()

        self.loop()

    @staticmethod
    def log(msg):
        print(msg, flush=True)

    def update_dialogs(self):
        # TODO: push event to self.update_queue
        event = Update(UpdateType.DIALOGUES_UPDATE)
        self.update_queue.put_nowait(event)

    def update_messages(self, id, from_id=None, to_id=None):
        # TODO: make this method work faster
        event = Update(UpdateType.MESSAGES_UPDATE, dialog_id=id)
        self.update_queue.put_nowait(event)

    def download_media(self, dialog_id, message_id):
        event = Update(UpdateType.MEDIA_DOWNLOAD, dialog_id=dialog_id, message_id=message_id,
                       download_handler=self.status.set_download)
        self.update_queue.put_nowait(event)
        print('added to queue')
