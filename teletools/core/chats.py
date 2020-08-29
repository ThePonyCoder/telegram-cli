import curses
import time

from ..classes.colors import Colors


# Интерфейсы:
# move_up
# move_down
# set_chat_list
# get_active_chat_id
# set_colors

class Chats:
    def __init__(self, window):

        self._window = window
        self._active_chat_id = None
        self._chat_list = None
        self._colors = Colors()
        self._visible_start = 0
        self._visible_end = 0

        self._active_chat_name = None

    def set_chat_list(self, chat_list):
        """
            chat_list = [
                {
                    name: "",
                    id: "",
                    flags: "-u",
                    unread_count: ""
                }
            ]
        :param chat_list:
        :return:
        """
        self._chat_list = chat_list
        self._draw_chats()

    def move_up(self, count=1):
        active_chat_pos = self._get_active_chat_pos()
        self._active_chat_id = self._chat_list[max(0, active_chat_pos - count)]['id']
        self._draw_chats()

    def move_down(self, count=1):
        active_chat_pos = self._get_active_chat_pos()
        self._active_chat_id = self._chat_list[min(active_chat_pos + count, len(self._chat_list) - 1)]['id']
        self._draw_chats()

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

    def get_active_chat_id(self):
        return self._active_chat_id

    def get_active_chat_name(self):
        return self._active_chat_name

    def set_active_chat_id(self, id):
        """This is used to recreate Object, but leave the selected chat the same"""
        self._active_chat_id = id
        self._draw_chats()

    def _update_viewrange(self):
        if self._active_chat_id not in [i['id'] for i in self._chat_list]:
            self._active_chat_id = self._chat_list[0]['id']

        pos = self._get_active_chat_pos()
        self._active_chat_name = self._chat_list[pos].get('name')
        if len(self._chat_list) < self._height:
            start = 0
            end = self._height
        else:
            start = pos - int(self._height / 2)
            end = pos + int(self._height / 2)

            if start < 0:
                start = 0
                end = self._height
            if len(self._chat_list) < end:
                end = len(self._chat_list)
                start = end - self._height
        self._visible_start = start
        self._visible_end = end

    def _get_active_chat_pos(self):
        lst = [idx for idx, it in enumerate(self._chat_list) if it['id'] == self._active_chat_id]
        return lst[0]

    @property
    def _height(self):
        return self._window.getmaxyx()[0]

    @property
    def _width(self):
        return self._window.getmaxyx()[1]

    def _draw_chats(self):
        self._update_viewrange()
        self._window.clear()
        for line, chat in enumerate(self._chat_list[self._visible_start:self._visible_end]):
            number = str(abs(line + self._visible_start - self._get_active_chat_pos()))
            flags = '[' + chat['flags'] + ']'
            name = f' {number:>2}  {flags} {chat["name"]}'.ljust(self._width)[:self._width - 1] + ' '
            name = name[:self._width - 1]
            name = name[:-len(chat['unread_count'])] + chat['unread_count']
            if chat['id'] == self._active_chat_id:
                self._window.addstr(line, 0, name, curses.A_BOLD | self._colors.dialog.selected)
            else:
                if chat['muted_until'] < time.time() and int(chat['unread_count']) > 0:
                    self._window.addstr(line, 0, name, curses.A_BOLD | self._colors.dialog.alert)
                else:
                    self._window.addstr(line, 0, name, curses.A_BOLD | self._colors.dialog.default)
        # self._window.refresh()
