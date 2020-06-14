import sys


class Messages:
    def __init__(self, window):
        self.window = window
        self.colors = None
        self.message_list = None
        self.active_msg = None

    def set_message_list(self, message_list):
        self.message_list = message_list
        self._draw_messages()

    def _draw_messages(self):
        self.window.clear()
        line = self.height - 1
        for msg in self.message_list:
            if not msg.text:
                msg.text = ''
            splited = self.split_msg(msg.text)
            if msg.text == '':
                splited = ['[content]']
            while line >= 0 and len(splited):
                self.window.insstr(line, 0, splited[-1])
                splited = splited[:-1]
                line -= 1
            line -= 1

        self.window.refresh()

    def split_msg(self, text):
        text = text.strip()
        lines = text.split('\n')
        out = []
        for text in lines:
            text = text.split()
            ret = ['']
            for i in text:
                if len(i) > self.width:
                    while len(i):
                        ret.append(i[:self.width])
                        i = i[self.width:]
                if len(i) + len(ret[-1]) > self.width:
                    ret.append('')
                ret[-1] = ret[-1] + ' ' + i if ret[-1] else i
            out = out + ret
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

