import sys
import curses
from pprint import pprint
import time
from ..classes.modes import DRAWMODE
from ..classes.modes import Colors
import unicodedata


class Messages:
    def __init__(self, window):
        self.window = window  # curses.window
        self.colors = Colors()  # color palette
        self.message_list = None
        self.active_msg = None
        self.drown_number = 0  # number of messages that are drown on the screen
        self._last_drown_id = 0  # TODO: needs normal name. func too

    def set_message_list(self, message_list):
        """message_list = {
            id: mustbe,
            title: mustbe,
            flags: mustbe,
            data: mustbe,
            text: ~,
            date: ~,
        }
        """
        self.message_list = message_list
        self._last_drown_id = self.message_list[0].get('id')
        print(self._last_drown_id)
        self._draw_messages()

    @staticmethod
    def _get_time(timestamp):
        time_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(timestamp))
        return time_str

    def _create_title(self, msg):
        """
        msg = {
            id: mustbe,
            title: mustbe,
            flags: mustbe,
            data: mustbe,
        }
        """
        title_left = str(msg.get('title'))

        title_right = str(msg.get('id')) + ' '

        title_right += '[' + msg.get('flags') + '] '

        title_right += self._get_time(msg['date'])
        title = title_left.ljust(self.width - self.__count_wide_unicode_chars(title_left))[:-len(title_right)] \
                + title_right
        return title

    @staticmethod
    def __count_wide_unicode_chars(s):
        ans = 0
        try:
            for i in s:
                if unicodedata.east_asian_width(i) == 'W':
                    ans += 1
        except TypeError:
            pass
        return ans

    def _draw_messages(self):
        self.window.clear()
        line = self.height - 1
        self.drown_number = 0

        for msg in self.message_list:
            if msg.get('mediatype') and line >= 0:
                self.window.insstr(line, 0, f'[{msg.get("mediatype")}]', self.colors.message.media)
                line -= 1

            if msg.get('text'):
                splited = self._split_msg(msg.get('text'))
                while line >= 0 and len(splited):
                    self.window.insstr(line, 0, splited[-1], self.colors.message.default)
                    splited = splited[:-1]
                    line -= 1

            if line >= 0:
                title = self._create_title(msg)
                self.window.insstr(line, 0, str(title), self.colors.message.author)
            line -= 2
            if line < 0:
                break
            self.drown_number += 1

        self.window.refresh()

    def _split_msg(self, text):
        if not isinstance(text, str):
            return ''
        text = text.strip()
        lines = [i for i in text.split('\n') if i != '']
        out = []

        for text in lines:
            text = text.split()
            ret = ['']
            for i in text:
                i = i.replace(u'\u200b', '')
                if len(i) > self.width:
                    while len(i):
                        ret.append(i[:self.width])
                        i = i[self.width:]
                if len(i) + len(ret[-1]) + 1 > self.width:
                    ret.append('')
                ret[-1] = ret[-1] + ' ' + i if ret[-1] else i
            out = out + ret
        while len(out) >= 1 and out[0] == '':
            out = out[1:]
        return out

    @property
    def height(self):
        return self.window.getmaxyx()[0]

    @property
    def width(self):
        return self.window.getmaxyx()[1]

    def set_colors(self, colors):
        pass
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

    def get_last_drown_id(self):
        """Returns the id of last drown message"""
        return self._last_drown_id

    # def _update_active_msg(self):
    #     """This function helps to keep active msg when updating message list"""
    #
    #     for i in self.message_list:
    #         if self.active_msg is None and i.mode == DRAWMODE.SELECTED:
    #             i.mode  = DRAWMODE.DEFAULT
    #         if self.active_msg is None:
    #             continue
    #         elif i.message == self.active_msg.message:
    #             i.mode = DRAWMODE.SELECTED
    #         elif i.mode == DRAWMODE.SELECTED:
    #             i.mode = DRAWMODE.DEFAULT

    # def move_up(self):
    #     if self.active_msg is None:
    #         self.active_msg = self.message_list[0]
    #     if self.shift < self.message_list.__len__():
    #         self.shift += 1
    #
    #     if self.active_msg_index < (len(self.message_list) - 1):
    #         self.active_msg = self.message_list[self.active_msg_index + 1]
    #         self._update_active_msg()
    #     self._draw_messages()

    # def move_down(self):
    #     if self.active_msg is None:
    #         return
    #     if self.shift > 0:
    #         self.shift -= 1
    #     if self.active_msg_index > 0:
    #         self.active_msg = self.message_list[self.active_msg_index - 1]
    #         self._update_active_msg()
    #     else:
    #         self.active_msg = None
    #     self._draw_messages()
