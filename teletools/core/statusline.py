import sys
import curses
from pprint import pprint
import time
from ..classes.modes import DRAWMODE, Colors


class Status:
    def __init__(self, window):
        self._window = window  # curses.window
        self._colors = Colors()  # color palette
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

        self._window.insstr(dialogstr, self._colors.status.dialog_name | curses.A_BOLD)

        self._window.insstr(modestr, self._colors.status.mode | curses.A_BOLD)

        self._window.insstr(0, self._width - len(newmsgstr), newmsgstr)
        self._window.addstr(0, self._width - len(newmsgstr) - len(numberkitstr), numberkitstr)
        self._window.refresh()
        pass

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
        self._colors = colors

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
        pass
        self._colors = colors
