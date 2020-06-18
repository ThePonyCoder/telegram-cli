import sys
import curses
from ..classes.modes import DRAWMODE


class Messages:
    def __init__(self, window):
        self.window = window  # curses.window
        self.colors = None  # color palette
        self.message_list = None  # list of Message objects
        self.active_msg = None  # Message object
        self.shift = None  # draw message_list with this shift
        self.drown_number = 0  # number of messages that are drown on the screen

    # def selection_toggle(self):
    #     if self.active_msg is None:
    #         self.active_msg = self.message_list[0]
    #     else:
    #         self.active_msg = None
    #     self._update_active_msg()

    def set_message_list(self, message_list):
        """message_list - list of Message from classes.message"""
        self.message_list = message_list
        self._update_active_msg()
        self.shift = 0
        self._draw_messages()

    def _update_active_msg(self):
        """This function helps to keep active msg when updating message list"""

        for i in self.message_list:
            if self.active_msg is None and i.mode == DRAWMODE.SELECTED:
                i.mode  = DRAWMODE.DEFAULT
            if self.active_msg is None:
                continue
            elif i.message == self.active_msg.message:
                i.mode = DRAWMODE.SELECTED
            elif i.mode == DRAWMODE.SELECTED:
                i.mode = DRAWMODE.DEFAULT

    def move_up(self):
        if self.active_msg is None:
            self.active_msg = self.message_list[0]
        if self.shift < self.message_list.__len__():
            self.shift += 1

        if self.active_msg_index < (len(self.message_list) - 1):
            self.active_msg = self.message_list[self.active_msg_index + 1]
            self._update_active_msg()
        self._draw_messages()

    def move_down(self):
        if self.active_msg is None:
            return
        if self.shift > 0:
            self.shift -= 1
        if self.active_msg_index > 0:
            self.active_msg = self.message_list[self.active_msg_index - 1]
            self._update_active_msg()
        else:
            self.active_msg = None
        self._draw_messages()

    @property
    def active_msg_index(self):
        return self.message_list.index(self.active_msg)

    def _draw_messages(self):
        self.window.clear()
        line = self.height - 1
        self.drown_number = 0
        for msg in self.message_list[self.shift:]:
            splited = self.split_msg(msg.text)
            if msg.text == '':
                splited = ['[content]']

            while line >= 0 and len(splited):
                self.window.insstr(line, 0, splited[-1], self.colors[msg.mode])
                splited = splited[:-1]
                line -= 1
            if line >= 0:
                self.window.addstr(line, 0, msg.title, self.colors['author'])
            line -= 2
            if line < 0:
                break
            self.drown_number += 1

        self.window.refresh()

    def split_msg(self, text):
        if not isinstance(text, str):
            return ''
        text = text.strip()
        lines = [i for i in text.split('\n') if i != '']
        out = []
        with open('echo.txt', 'r+') as f:
            f.write('\n'.join(lines))
        for text in lines:
            text = text.split()
            ret = ['']
            for i in text:
                if len(i) > self.width:
                    while len(i):
                        ret.append(i[:self.width])
                        i = i[self.width:]
                if len(i) + len(ret[-1]) + 1 > self.width:
                    ret.append('')
                ret[-1] = ret[-1] + ' ' + i if ret[-1] else i
            out = out + ret
        if len(out) >= 2 and out[0] == '': out = out[1:]
        return out

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

    def clear(self):
        self.window.clear()
        self.window.refresh()
