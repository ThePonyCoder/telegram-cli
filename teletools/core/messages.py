import sys
import curses


class Messages:
    def __init__(self, window):
        self.window = window
        self.colors = None
        self.message_list = None
        self.active_msg = None
        self.shift = None

    def set_message_list(self, message_list):
        self.message_list = message_list
        self.shift = 0
        self._draw_messages()

    def move_up(self):
        if self.shift < self.message_list.__len__():
            self.shift += 1
        self._draw_messages()

    def move_down(self):
        if self.shift > 0:
            self.shift -= 1
        self._draw_messages()

    def _draw_messages(self):
        self.window.clear()
        line = self.height - 1
        for msg in self.message_list[self.shift:]:
            splited = self.split_msg(msg.text)
            if msg.text == '':
                splited = ['[content]']

            while line >= 0 and len(splited):
                self.window.insstr(line, 0, splited[-1])
                splited = splited[:-1]
                line -= 1
            if line >= 0:
                self.window.addstr(line, 0, msg.title, self.colors['author'])
            line -= 2
            if line < 0:
                break

        self.window.refresh()

    def split_msg(self, text):
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
