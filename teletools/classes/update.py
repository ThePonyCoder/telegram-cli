from enum import Enum, auto


class Update:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class UpdateType(Enum):
    MESSAGES_UPDATE = auto()
    DIALOGUES_UPDATE = auto()
    MEDIA_DOWNLOAD = auto()
