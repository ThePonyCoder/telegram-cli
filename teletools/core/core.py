import string
import curses
import curses.textpad
import queue
import threading
import time
import os

from .chats import Chats
from .messages import Messages
from ..classes.colors import Colors
from ..classes.modes import MODES
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
        self.writer_window = None

        self.draft = ''  # support inserting text
        self.mode = MODES.DEFAULT

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

            self.new_data_event.wait()
            self.draw_chats(noupdate=True)
            self.draw_messages(noupdate=True)
            self.new_data_event.clear()
            print('new_event')

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
        self.writer_window = writer_window

        # writer_window.border(0, 0, 0, 0)
        writer_window.refresh()

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

        reduced_chat_list.insert(0, {'name': 'Archived chats',
                                     'id': 0,
                                     'flags': '-f'
                                     })  # This is archive folder!
        self.chats.set_chat_list(reduced_chat_list)

    def __get_active_id(self):
        return self.chats.get_active_chat_id()

    def draw_messages(self, noupdate=False):
        if self.__get_active_id() == 0:  # checking archive folder
            self.messages.clear()
            self.status.set_dialog_name('Archive')
            return
        if not noupdate:
            self.update_messages(self.__get_active_id())
        messages_list = self.database.get_messages(self.__get_active_id())

        def _get_flags(msg):
            flags = ''
            flags += 'r' if msg.get('is_reply') else '-'
            flags += 'f' if msg.get('forward') else '-'
            return flags

        def _get_media_type(msg):
            if msg.get('photo'):
                return 'photo'
            if msg.get('audio'):
                return 'audio'
            if msg.get('video'):
                return 'video'
            if msg.get('voice'):
                return 'voice'
            if msg.get('file'):
                return 'file'
            if msg.get('gif'):
                return 'gif'
            if msg.get('sticker'):
                return 'sticker'
            if msg.get('poll'):
                return 'poll'
            return None

        reduced_message_list = []
        for i in messages_list:
            reply_to_text = ''
            reply_to_title = ''
            if i['is_reply']:
                reply_to_id = i['reply_to_msg_id']
                reply_to_msg = self.database.get_messages(dialog_id=self.__get_active_id(),
                                                          limit=1,
                                                          max_id=reply_to_id,
                                                          min_id=reply_to_id)
                if reply_to_msg:
                    reply_to_text = reply_to_msg[0]['message']
                    reply_to_title = reply_to_msg[0]['from_name']

            reduced_msg = {
                # 'title': str(self.database.get_user_name(i['from_id'])[1]),
                'title': i['from_name'],
                'id': i['id'],
                'flags': _get_flags(i),
                'text': i['message'],
                'date': i['date'],
                'mediatype': _get_media_type(i),
                'is_reply': i['is_reply'],
                'reply_to_id': i['reply_to_msg_id'],
                'reply_to_text': reply_to_text,
                'reply_to_title': reply_to_title
            }
            reduced_message_list.append(reduced_msg)

        self.messages.set_message_list(reduced_message_list)
        self.status.set_dialog_name(self.chats.get_active_chat_name())

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

    def insert(self):
        curses.curs_set(1)
        self.status.set_mode(MODES.INSERT)
        pad = curses.textpad.Textbox(self.writer_window)
        pad.edit()
        self.draft = pad.gather()
        curses.curs_set(0)
        self.status.set_mode(MODES.DEFAULT)

    def send_message(self):
        if self.draft == '':
            return
        self.update_queue.put_nowait(Update(
            type=UpdateType.SEND_MESSAGE,
            dialog_id=self.__get_active_id(),
            message=self.draft
        ))
        self.draft = ''
        self.writer_window.clear()
        self.writer_window.refresh()

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
        if not key:
            return
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

        if key == 'i':
            self.insert()

        if key == '\n':
            self.send_message()

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
            self.key_handler(ch)
            print(repr(ch))

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
        event = Update(type=UpdateType.DIALOGUES_UPDATE)
        self.update_queue.put_nowait(event)

    def update_messages(self, id, from_id=None, to_id=None, ids=None):
        # TODO: make this method work faster
        event = Update(type=UpdateType.MESSAGES_UPDATE, dialog_id=id, ids=ids)
        self.update_queue.put_nowait(event)

    def download_media(self, dialog_id, message_id):
        event = Update(type=UpdateType.MEDIA_DOWNLOAD, dialog_id=dialog_id, message_id=message_id,
                       download_handler=self.status.set_download)
        self.update_queue.put_nowait(event)
        print('added to queue')
