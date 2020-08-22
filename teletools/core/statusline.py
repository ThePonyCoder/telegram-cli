import sys
import curses
from pprint import pprint
import time
from ..classes.modes import DRAWMODE


class Status:
    def __init__(self, window):
        self._window = window  # curses.window
        self._colors = None  # color palette
        self._char_query = ''
        self._new_messages_counter = 0
        self._mode = 'DIALOGS'
        self._dialog_name = 'None'

    def set_char_query(self, char_query):
        self._char_query = char_query
        self._update()

    def set_mode(self, mode):
        self._mode = mode
        self._update()

    def set_dialog_name(self, dialog_name):
        self._dialog_name = dialog_name
        self._update()

    def set_newmessage_counter(self, new_messages_counter):
        self._new_messages_counter = new_messages_counter
        self._update()

    def _update(self):
        # TODO: partial updates to save performance
        self._window.clear()
        modestr = f' {self._mode} '
        dialogstr = f' {self._dialog_name} '
        newmsgstr = f' [{self._new_messages_counter}] '
        numberkitstr = f' {self._char_query} '

        curses.init_color(123, 686, 843, 529)

        curses.init_pair(125, 123, curses.COLOR_BLACK)
        self._window.insstr(dialogstr, curses.color_pair(125) | curses.A_BOLD)

        curses.init_pair(124, curses.COLOR_BLACK, 123)
        self._window.insstr(modestr, curses.color_pair(124) | curses.A_BOLD)

        self._window.insstr(0, self._width - len(newmsgstr), newmsgstr)
        self._window.addstr(0, self._width - len(newmsgstr) - len(numberkitstr), numberkitstr)
        self._window.refresh()
        pass

    def set_colors(self, colors):
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
        self._window.clear()
        self._window.refresh()

    @property
    def _height(self):
        return self._window.getmaxyx()[0]

    @property
    def _width(self):
        return self._window.getmaxyx()[1]

    def set_colors(self, colors):
        self.colors = colors
