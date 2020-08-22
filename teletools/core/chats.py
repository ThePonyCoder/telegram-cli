import curses


# Интерфейсы:
# move_up
# move_down
# set_chat_list
# get_active_chat_id
# set_colors

class Chats:
    def __init__(self, window):
        """

        """
        self._window = window
        self._active_chat_id = None
        self._chat_list = None
        self._colors = None
        self._visible_start = 0
        self._visible_end = 0

    def set_chat_list(self, chat_list):
        """
            chat_list = [
                {
                    name: "",
                    id: "",
                    flags: "-u"
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

    def set_active_chat_id(self, id):
        self._active_chat_id = id
        self._draw_chats()

    def _update_viewrange(self):
        if self._active_chat_id not in [i['id'] for i in self._chat_list]:
            self._active_chat_id = self._chat_list[0]['id']

        pos = self._get_active_chat_pos()
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
        self._window.erase()
        for line, chat in enumerate(self._chat_list[self._visible_start:self._visible_end]):
            flags = '[' + chat['flags'] + ']'
            name = (flags + chat['name']).ljust(self._width)[:self._width - 1] + ' '
            if chat['id'] == self._active_chat_id:
                self._window.insstr(line, 0, name, curses.A_BOLD | self._colors['active'])
            else:
                self._window.insstr(line, 0, name, curses.A_BOLD | self._colors['inactive'])

        self._window.refresh()
