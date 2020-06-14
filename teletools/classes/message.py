import string
from enum import Enum, auto

class MESSAGE_TYPE(Enum):
    TEXT = auto()
    PHOTO = auto()
    LINK = auto()
    FILE = auto()


class Message:
    def __init__(self, message, entity=None, chat=None):
        self.message = message
        self.entity = entity
        self.chat = chat


    @property
    def id(self):
        return self.message.id

    @property
    def text(self):
        return self.message.text

    @property
    def title(self):
        if self.entity:
            if 'title' in self.entity.__dict__:
                return self._deunicode(self.entity.title)
            title = ''
            if 'first_name' in self.entity.__dict__ and self.entity.first_name:
                title += self.entity.first_name
            if 'last_name' in self.entity.__dict__ and self.entity.last_name:
                title += ' ' if title else ''
                title += self.entity.last_name
            return self._deunicode(title)
        else:
            return self._deunicode(self.chat.title)

    @staticmethod
    def _deunicode(text):
        return text
        # printable = set(string.printable)
        # return ''.join(filter(lambda x: x in printable, text))

    @property
    def from_username(self):
        return 'TODO'

