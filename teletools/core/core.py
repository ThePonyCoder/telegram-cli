import curses

ACTIVE_CHAT = 1
INACTIVE_CHAT = 2
ALERT = 3


def init_colors():
    curses.start_color()
    curses.init_pair(ACTIVE_CHAT, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(INACTIVE_CHAT, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(ALERT, curses.COLOR_BLACK, curses.COLOR_RED)

def init_windows():
    main_window = curses.initscr()



def init():
    init_colors()
    init_windows()
