from enum import Enum, auto


class Update:
    def __init__(self, type, dialog_id=None, offset=0):
        self.type = type
        self.dialog_id = dialog_id
        self.offset = offset

        # checking if dialogue
        if self.type == UpdateType.MESSAGES_UPDATE and self.dialog_id is None:
            raise Exception('You must specify dialog_id, if the type is MESSAGES_UPDATE')
            # TODO: write normal exception


class UpdateType(Enum):
    MESSAGES_UPDATE = auto()
    DIALOGUES_UPDATE = auto()
