from enum import Enum, auto


class CHAT_TYPE(Enum):
    CHAT = auto()
    BOT = auto()
    GROUP = auto()


class Chat:
    def __init__(self, chat, is_archive = False):
        """
        :param chat: if chat is None than this chat is archive folder
        """
        self.chat = chat

    @property
    def name(self):
        if self.chat is None:
            return '[Archived chats]'
        return self.chat.name

    @property
    def id(self):
        if self.chat is None:
            return 0
        return self.chat.id

    @property
    def archived(self):
        if self.chat is None:
            return False
        return self.chat.archived
