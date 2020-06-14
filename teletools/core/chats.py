from math import trunc
from time import sleep
import curses


class Chats:
    def __init__(self, window):
        self.window = window
        self.active_chat = None
        self.chat_list = None
        self.colors = None

    def set_chat_list(self, chat_list):
        self.chat_list = chat_list
        if self.active_chat is None:
            self.active_chat = self.chat_list[0]

        self._draw_chats(0, self.height)

    def _draw_chats(self, start=0, end=1):
        self.window.erase()
        for line, chat in enumerate(self.chat_list[start:end]):
            if chat == self.active_chat:
                self.window.insstr(line, 0, chat.name.ljust(self.width), curses.A_BOLD | self.colors['active'])
            else:
                self.window.insstr(line, 0, chat.name.ljust(self.width), curses.A_BOLD | self.colors['inactive'])

        self.window.refresh()

    def move_up(self):
        active_chat_pos = self.chat_list.index(self.active_chat)
        if active_chat_pos == 0:
            return
        self.change_active(active_chat_pos - 1)

    def move_down(self):
        active_chat_pos = self.chat_list.index(self.active_chat)
        self.window.erase()

        if active_chat_pos == len(self.chat_list)-1:
            return
        self.change_active(active_chat_pos + 1)

    def change_active(self, pos):
        start, end = None, None
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
        # print(start,end)
        self.active_chat = self.chat_list[pos]
        self._draw_chats(start,end)



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
