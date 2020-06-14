from enum import Enum, auto


class MESSAGE_TYPE(Enum):
    TEXT = auto()
    PHOTO = auto()
    LINK = auto()
    FILE = auto()


class Message:
    def __init__(self, id, text, message, type=MESSAGE_TYPE.TEXT):
        self.id = id
        self.type = type
        self.content = message
        self.text = text
