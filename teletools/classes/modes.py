from enum import Enum, auto


class MODE(Enum):
    ARCHIVED = auto()
    CHATS = auto()
    MESSAGES = auto()


class DRAWMODE(Enum):
    SELECTED = auto()
    DEFAULT = auto()
