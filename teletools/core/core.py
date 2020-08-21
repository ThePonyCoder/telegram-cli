import string
import curses
import curses.textpad
import queue
import threading

from .chats import Chats
from .messages import Messages
from ..classes.modes import DRAWMODE, FOLDER
from ..classes.modes import MODE
from ..tools.database import Database
from ..classes.update import Update, UpdateType

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

        self.mode = MODE.CHATS
        self.folder = FOLDER.DEFAULT

        # synchronisation between threads
        self.new_data_event = new_data_event
        self.update_queue = update_queue

        # Digits
        self.number_kit = ''  # TODO: better name

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

    def draw_messages(self, noupdate=False):
        if self.chats.get_active_chat_id() == 0:  # checking archive folder
            self.messages.clear()
            return
        if not noupdate:
            self.update_messages(self.chats.get_active_chat_id())
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

        COLORS = {  # TODO: make normal colors defenitions
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

    def key_handler(self, key):
        if key in string.digits:
            self.number_kit += key
            # TODO: drawn number status
        print(self.number_kit)
        if key == 'j':
            self.chats.move_down(int(self.number_kit) if self.number_kit else 1)
            self.draw_messages()
        if key == 'k':
            self.chats.move_up(int(self.number_kit) if self.number_kit else 1)
            self.draw_messages()

        if key == 'q':
            self.exit()
            return

        # if key == ord('i'):
        #     # insert mode
        #     pass
        if key == 'R':
            self.redraw()
        # time.sleep(0.2)
        if key not in string.digits:
            self.number_kit = ''

    def loop(self):
        while True:
            ch = self.main_window.getkey()
            # print(ch)
            self.key_handler(ch)

            if self.new_data_event.is_set():
                self.draw_chats(noupdate=True)
                self.draw_messages(noupdate=True)
                self.new_data_event.clear()

    def exit(self, code=0):
        self.main_window.clear()
        self.main_window.refresh()

    def run(self):
        self.draw_chats()
        self.draw_messages()

        self.loop()

    @staticmethod
    def log(msg):
        print(msg, flush=True)

    def update_dialogs(self):
        # TODO: push event to self.update_queue
        event = Update(UpdateType.DIALOGUES_UPDATE)
        self.update_queue.put_nowait(event)

    def update_messages(self, id, from_id=None, to_id=None):
        # TODO: push event to self.update_queue
        event = Update(UpdateType.MESSAGES_UPDATE, dialog_id=id)
        self.update_queue.put_nowait(event)
        print(self.update_queue.qsize())
