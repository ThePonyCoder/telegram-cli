from enum import Enum, auto


class MESSAGE_TYPE(Enum):
    TEXT = auto()
    PHOTO = auto()
    LINK = auto()


class Message:
    def __init__(self, id, message, type):
        self.id = id
        self.type = type
        self.content = message
