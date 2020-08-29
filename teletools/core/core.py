import _curses
import curses
import curses.textpad
import math
import os
import queue
import string
import threading
import time

from .chats import Chats
from .messages import Messages
from .statusline import Status
from .writer import Writer
from ..classes.modes import MODES
from ..classes.update import Update, UpdateType
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
    def __init__(self, new_data_event: threading.Event, update_queue: queue.Queue):
        self.database = Database()

        # curses windows
        self.main_window = None
        self.chats = None
        self.messages = None
        self.status = None
        self.writer = None

        self.draft = ''  # support inserting text
        self.mode = MODES.DEFAULT

        # synchronisation between threads
        self.new_data_event = new_data_event
        self.update_queue = update_queue
        self.last_update_time = 0

        # many actions at a time
        self.char_query = ''

        self.init_windows()

        threading.Thread(target=self.continuous_updates).start()

    def continuous_updates(self):
        while True:
            # self.main_window.refresh()

            self.new_data_event.wait()
            if (time.time() - self.last_update_time) <= 0.2:
                print('sleeping timeout')
                time.sleep(0.2 - (time.time() - self.last_update_time))

            print('new_EVENT!!!')
            self.draw_chats(noupdate=True)
            self.draw_messages(noupdate=True)
            self.new_data_event.clear()
            self.last_update_time = time.time()
            self.refresh()

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

        self.main_window.idcok(True)
        status_window.idcok(True)
        writer_window.idcok(True)
        messages_window.idcok(True)

        self.main_window.idlok(True)
        status_window.idlok(True)
        writer_window.idlok(True)
        messages_window.idlok(True)

        self.chats = Chats(chats_window)
        self.messages = Messages(messages_window)
        self.status = Status(status_window)
        self.writer = Writer(writer_window)

        # writer_window.border(0, 0, 0, 0)
        writer_window.refresh()

    def draw_chats(self, noupdate=False):
        if not noupdate:
            self.update_dialogs()
        # print('chats_redrawing')
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

        reduced_chat_list = []
        for chat in chat_list:
            unread_count = -1
            try:
                unread_count = chat['unread_count']
            except Exception as e:
                print("Can't calculate unread_count", e)

            reduced_chat_list.append({
                'name': chat['name'],
                'id': chat['id'],
                'flags': _get_chat_flags(chat),
                'unread_count': str(unread_count),
                'muted_until': chat['muted_until']
            })

        reduced_chat_list.insert(0, {'name': 'Archived chats',
                                     'id': 0,
                                     'flags': '-f',
                                     'unread_count': '0',
                                     'muted_until': math.inf
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
            self.update_messages(id=self.__get_active_id())
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

        self.refresh()

        # self.chats.set_colors(COLORS)
        # self.messages.set_colors(COLORS)
        # self.status.set_colors(COLORS)

    def send_message(self):
        draft = self.writer.get_draft()
        if draft == '':
            return
        self.update_queue.put_nowait(Update(
            type=UpdateType.SEND_MESSAGE,
            dialog_id=self.__get_active_id(),
            message=draft
        ))
        self.writer.clear()

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

    def insert_key_handler(self, s):
        if s == '^J':
            s = '\n'

        if s == '^[':
            self._leave_insert_mode()

        elif s == '^[[D':
            self.writer.curs_left()

        elif s == '^[[C':
            self.writer.curs_right()

        elif s == '^[[A':
            self.writer.curs_up()

        elif s == '^[[B':
            self.writer.curs_down()

        elif s == '^?':
            self.writer.rm()

        elif len(s) == 1:
            self.writer.addch(s)
        self.refresh()

    @staticmethod
    def _unctr(char):
        try:
            unctr = curses.unctrl(char)
            return unctr
        except OverflowError:
            return ''

    def _enter_insert_mode(self):
        self.mode = MODES.INSERT
        self.status.set_mode(MODES.INSERT)

    def _leave_insert_mode(self):
        self.mode = MODES.DEFAULT
        self.status.set_mode(MODES.DEFAULT)

    def key_handler(self, s):
        if not s:
            return

        if self.mode == MODES.INSERT:
            self.insert_key_handler(s)
            return

        if isinstance(s, str) and len(s) == 1 and s in string.digits:
            self.update_query(s)

        if s == 'j':
            self.chats.move_down(int(self.char_query) if self.char_query else 1)
            self.draw_messages()
        if s == 'k':
            self.chats.move_up(int(self.char_query) if self.char_query else 1)
            self.draw_messages()

        if s == 'q':
            self.exit()
            return

        if s == 'i':
            self._enter_insert_mode()

        if s == '^J':
            self.send_message()

        if s == 'o' and self.char_query != '':
            self.download_media(self.__get_active_id(), int(self.char_query))

        if s == 'r':
            self.mark_as_read(self.__get_active_id())

        if s == 'R' or s == '~Z':
            self.redraw()

        if isinstance(s, str) and len(s) == 1 and s not in string.digits:
            self.update_query()

    def loop(self):
        while True:
            wch = self.main_window.get_wch()

            # handling escape sequences
            try:
                s = curses.unctrl(wch)
                if s.decode() == '^[':
                    self.main_window.nodelay(True)
                    while True:
                        try:
                            s += self._unctr(self.main_window.get_wch())
                        except _curses.error:
                            break
                    self.main_window.nodelay(False)
                s = s.decode()
            except OverflowError or LookupError:
                print('overflow')
                s = wch

            # print(s)

            self.key_handler(s)
            self.refresh()

    def refresh(self):
        self.main_window.touchwin()
        self.main_window.refresh()

    def update_query(self, char=None):
        if char is None:
            self.char_query = ''
        else:
            self.char_query += char
        self.status.set_char_query(self.char_query)

    def exit(self, code=0):
        curses.endwin()
        os._exit(0)

    def run(self):

        self.draw_chats()
        self.draw_messages()
        self.status._update()
        self.refresh()

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
        print('added to queue downloadmedia event')

    def mark_as_read(self, dialog_id):
        event = Update(type=UpdateType.READ_MESSAGE, dialog_id=dialog_id)
        self.update_queue.put_nowait(event)
        print('added set as read')
