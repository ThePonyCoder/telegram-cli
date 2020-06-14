from ..classes.chat import Chat
from telethon import TelegramClient
from pprint import pprint


class TelegramApi:
    def __init__(self, api_id, api_hash):
        self.client = TelegramClient('session', api_id, api_hash)
        self.client.start()

    def get_chats(self):
        async def get_chat_list(self):
            return await self.client.get_dialogs()

        chat_list = self.client.loop.run_until_complete(get_chat_list(self))

        chat_list = [Chat(i.id, i.name, i) for i in chat_list]
        return chat_list


def auth():
    pass

def get_messages():
    pass


if __name__ == '__main__':
    # client = TelegramApi()
    client.get_chats()
