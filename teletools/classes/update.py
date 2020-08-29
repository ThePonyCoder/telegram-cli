from enum import Enum, auto


class Update:
    """
    Update usually have type, dialog_id and others
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class UpdateType(Enum):
    MESSAGES_UPDATE = auto()
    DIALOGUES_UPDATE = auto()
    MEDIA_DOWNLOAD = auto()
    SEND_MESSAGE = auto()
    READ_MESSAGE = auto()
