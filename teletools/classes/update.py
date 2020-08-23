from enum import Enum, auto


class Update:
    def __init__(self, type, dialog_id=None, offset=0, message_id=None, download_handler=None):
        self.message_id = message_id
        self.type = type
        self.dialog_id = dialog_id
        self.offset = offset
        self.download_handler = download_handler


class UpdateType(Enum):
    MESSAGES_UPDATE = auto()
    DIALOGUES_UPDATE = auto()
    MEDIA_DOWNLOAD = auto()
