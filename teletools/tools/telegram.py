from ..classes.chat import Chat
from ..classes.message import Message
from telethon import TelegramClient
from pprint import pprint


class TelegramApi:
    def __init__(self, api_id, api_hash):
        self.client = TelegramClient('session', api_id, api_hash)
        self.client.start()

    def get_chats(self):
        async def get_chats(self):
            return await self.client.get_dialogs()

        chats = self.client.loop.run_until_complete(get_chats(self))

        chats = [Chat(i.id, i.name, i) for i in chats]
        return chats

    def get_messages(self, id):
        async def get_messages(self, id):
            return await self.client.get_messages(id,limit=20)

        messages = self.client.loop.run_until_complete(get_messages(self, id))
        data = []
        for i in messages:
            data.append(Message(i.id, i.text, i))
        return data


def auth():
    pass


def get_messages():
    pass


if __name__ == '__main__':
    # client = TelegramApi()
    client.get_chats()
