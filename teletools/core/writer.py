class Writer:
    def __init__(self, window):
        self.window = window
        self.draft = []

    def clear(self):
        self.window.clear()
        self.window.refresh()
        self.draft = []

    def addch(self, char):
        self.window.addch(char)
        self.window.refresh()
        self.draft.append(char)

    def prev(self):
        pass

    def next(self):
        pass

    def rm(self):
        y, x = self.window.getyx()

        if x == 0 and y == 0:
            pass
        elif x == 0 and y != 0:
            y -= 1
            x = self._width - 1
        else:
            x -= 1

        self.window.delch(y, x)
        self.window.move(y, x)
        self.window.refresh()

        if self.draft:
            self.draft.pop()

    def get_draft(self):
        return ''.join(self.draft)

    @property
    def _height(self):
        return self.window.getmaxyx()[0]

    @property
    def _width(self):
        return self.window.getmaxyx()[1]
