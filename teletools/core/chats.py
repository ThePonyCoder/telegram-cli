from math import trunc
from time import sleep
import curses


class Chats:
    def __init__(self, window):
        self.window = window
        self.active_chat = None
        self.chat_list = None
        self.colors = None
        self.start = 0
        self.end = 0

    def set_chat_list(self, chat_list):
        self.chat_list = chat_list
        self._draw_chats()

    def _draw_chats(self):
        self.update_viewrange()
        self.window.erase()
        for line, chat in enumerate(self.chat_list[self.start:self.end]):
            status = self._get_chat_status(chat)
            name = (status + chat['name']).ljust(self.width)[:self.width-1] + ' '
            if chat == self.active_chat:
                self.window.insstr(line, 0, name, curses.A_BOLD | self.colors['active'])
            else:
                self.window.insstr(line, 0, name, curses.A_BOLD | self.colors['inactive'])

        self.window.refresh()

    @staticmethod
    def _get_chat_status(chat):
        status = ' ['
        status += 'p' if chat['pinned'] else '-'
        if chat['is_user']:
            status += 'u'
        elif chat['is_channel']:
            status += 'c'
        elif chat['is_group']:
            status += 'g'
        else:
            status += '-'
        status += '] '
        return status

    def move_up(self):
        active_chat_pos = self.chat_list.index(self.active_chat)
        if active_chat_pos == 0:
            return
        self.active_chat = self.chat_list[active_chat_pos - 1]
        self._draw_chats()

    def move_down(self):
        active_chat_pos = self.chat_list.index(self.active_chat)
        if active_chat_pos == len(self.chat_list) - 1:
            return
        self.active_chat = self.chat_list[active_chat_pos + 1]
        self._draw_chats()

    def update_viewrange(self):
        start, end = None, None
        if self.active_chat not in self.chat_list:
            self.active_chat = self.chat_list[0]

        pos = self.chat_list.index(self.active_chat)
        if len(self.chat_list) < self.height:
            start = 0
            end = self.height
        else:
            start = pos - int(self.height / 2)
            end = pos + int(self.height / 2)

            if start < 0:
                start = 0
                end = self.height
            if len(self.chat_list) < end:
                end = len(self.chat_list)
                start = end - self.height
        self.start = start
        self.end = end

    @property
    def active_id(self):
        if self.active_chat is not None:
            return self.active_chat['id']

    @property
    def height(self):
        return self.window.getmaxyx()[0]

    @property
    def width(self):
        return self.window.getmaxyx()[1]

    def init_colors(self, colors):
        """
        colors example:
            {
                'active': curses.pair_content(ACTIVE_CHAT),
                'inactive': curses.pair_content(INACTIVE_CHAT),
                'alert': curses.pair_content(ALERT)
            }
        """
        self.colors = colors
