import curses


class Writer:
    def __init__(self, window):
        self.window = window
        self.draft = []  # list of list of char
        self.crs = [0, 0]  # cursor
        self.redraw()

    def clear(self):
        self.draft = []
        self.crs = [0, 0]
        self.redraw()

    def addch(self, char):
        if not self.draft:
            self.draft.append([])
            self.crs = [0, 0]
        if char == '\n':
            self.draft.append([])
            self.curs_down()
        else:
            self.draft[self.crs[0]].insert(self.crs[1], char)
            self.curs_right()
        self.redraw()

    def redraw(self):
        line = 0
        self.window.clear()
        while line < self._height and line < len(self.draft):
            self.window.insstr(line, 0, ''.join(self.draft[line]))
            line += 1

        self.window.chgat(*self.crs, 1, curses.A_REVERSE)
        self.window.refresh()

    def curs_left(self):
        if not self.draft:
            self.crs = [0, 0]
            self.redraw()
            return
        self.crs = [self.crs[0], max(self.crs[1] - 1, 0)]
        self.redraw()

    def curs_right(self):
        if not self.draft:
            self.crs = [0, 0]
            self.redraw()
            return
        self.crs = [self.crs[0], min(self.crs[1] + 1,
                                     self._width - 1,
                                     len(self.draft[self.crs[0]]))]
        self.redraw()

    def curs_up(self):
        if not self.draft:
            self.crs = [0, 0]
            self.redraw()
            return
        self.crs[0] = max(self.crs[0] - 1, 0)
        self.crs[1] = min(len(self.draft[self.crs[0]]), self.crs[1])
        self.redraw()

    def curs_down(self):
        if not self.draft:
            self.crs = [0, 0]
            self.redraw()
            return
        self.crs[0] = min(self.crs[0] + 1, len(self.draft) - 1)
        self.crs[1] = min(len(self.draft[self.crs[0]]), self.crs[1])
        self.redraw()

    def rm(self):
        if self.draft:
            if self.draft[self.crs[0]]:
                if self.crs[1] != 0:
                    self.draft[self.crs[0]].pop(self.crs[1] - 1)
                    self.curs_left()
            else:
                self.draft.pop(self.crs[0])
                self.curs_up()
                # TODO
                self.crs[1] = self._width - 1
                self.curs_right()
        self.redraw()

    def get_draft(self):
        ans = ''
        for i in self.draft:
            ans += ''.join(i) + '\n'
        return ans

    @property
    def _height(self):
        return self.window.getmaxyx()[0]

    @property
    def _width(self):
        return self.window.getmaxyx()[1]
