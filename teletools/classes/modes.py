from enum import Enum, auto
import curses


class MODE(Enum):
    ARCHIVED = auto()
    CHATS = auto()
    MESSAGES = auto()


class DRAWMODE(Enum):
    SELECTED = auto()
    DEFAULT = auto()


class FOLDER(Enum):
    DEFAULT = auto()
    ARHIVED = auto()


class Object:
    pass


class Colors:
    def __init__(self):
        curses.start_color()

        self.message = Object()
        self.dialog = Object()  # selected, default, alert
        self.status = Object()

        self.color_num_gen = iter(range(10, 1000))  # generate color numbers
        self._BLACK = next(self.color_num_gen)
        self._GRAY = next(self.color_num_gen)
        self._WHITE = next(self.color_num_gen)
        self._BLUE = next(self.color_num_gen)
        self._CYAN = next(self.color_num_gen)
        self._GREEN = next(self.color_num_gen)
        self._ORANGE = next(self.color_num_gen)
        self._PINK = next(self.color_num_gen)
        self._PURPLE = next(self.color_num_gen)
        self._RED = next(self.color_num_gen)
        self._YELLOW = next(self.color_num_gen)

        self.pair_num_gen = iter(range(10, 1000))  # pair_number_generator

        self._init_colors()
        self._init_message_color()
        self._init_dialog_color()
        self._init_status_color()

    def _init_colors(self):
        # change default colors
        curses.init_color(curses.COLOR_BLACK, *self.__tocrgb((40, 42, 54)))
        curses.init_color(curses.COLOR_WHITE, *self.__tocrgb((139, 233, 253)))

        curses.init_color(self._BLACK, *self.__tocrgb((40, 42, 54)))
        curses.init_color(self._GRAY, *self.__tocrgb((68, 71, 90)))
        curses.init_color(self._WHITE, *self.__tocrgb((248, 248, 242)))
        curses.init_color(self._BLUE, *self.__tocrgb((98, 114, 164)))
        curses.init_color(self._CYAN, *self.__tocrgb((139, 233, 253)))
        curses.init_color(self._GREEN, *self.__tocrgb((80, 250, 123)))
        curses.init_color(self._ORANGE, *self.__tocrgb((255, 184, 108)))
        curses.init_color(self._PINK, *self.__tocrgb((255, 121, 198)))
        curses.init_color(self._PURPLE, *self.__tocrgb((189, 147, 249)))
        curses.init_color(self._RED, *self.__tocrgb((255, 85, 85)))
        curses.init_color(self._YELLOW, *self.__tocrgb((241, 250, 140)))

    def _init_message_color(self):
        self.__add_color(self.message, 'author', self._GREEN, self._BLACK)
        self.__add_color(self.message, 'default', self._WHITE, self._BLACK)
        self.__add_color(self.message, 'media', self._PINK, self._BLACK)
        self.__add_color(self.message, 'reply', self._ORANGE, self._BLACK)

    def _init_dialog_color(self):
        self.__add_color(self.dialog, 'selected', self._BLACK, self._CYAN)
        self.__add_color(self.dialog, 'default', self._BLUE, self._BLACK)
        self.__add_color(self.dialog, 'alert', self._BLACK, self._YELLOW)

    def _init_status_color(self):
        self.__add_color(self.status, 'mode', self._BLACK, self._GREEN)
        self.__add_color(self.status, 'dialog_name', self._GREEN, self._BLACK)
        self.__add_color(self.status, 'download', self._PURPLE, self._BLACK)

    @staticmethod
    def __tocrgb(rgb: tuple):
        """translates rgb colors to curses color format for curses.init_color"""
        curses_rgb = []
        for id, color in enumerate(rgb):
            curses_rgb.append(int(color / 255 * 1000))
        return tuple(curses_rgb)

    def __add_color(self, obj, name, background, foreground):
        num = next(self.pair_num_gen)
        curses.init_pair(num, background, foreground)
        obj.__dict__.update({name: curses.color_pair(num)})
