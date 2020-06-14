from enum import Enum, auto


class CHAT_TYPE(Enum):
    CHAT = auto()
    BOT = auto()
    GROUP = auto()


class Chat:
    def __init__(self, id, name, chat_obj ,type=CHAT_TYPE.CHAT):
        self.id = id
        self.name = name
        self.type = type
