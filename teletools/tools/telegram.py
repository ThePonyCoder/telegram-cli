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

        chats = [Chat(i) for i in chats]
        return chats

    def get_messages(self, id):
        async def get_messages(self, id):
            return await self.client.get_messages(id, limit=10)

        async def get_entity(self, ids):
            return await self.client.get_entity(ids)

        messages = self.client.loop.run_until_complete(get_messages(self, id))
        data = []
        from_message_ids = [i.from_id if i.post is False else 'me' for i in messages]
        message_entities = self.client.loop.run_until_complete(get_entity(self, from_message_ids))
        chat = self.client.loop.run_until_complete(get_entity(self, id))
        for msg, entity in zip(messages, message_entities):
            entity = None if msg.post is True else entity
            data.append(Message(message=msg, entity=entity, chat=chat))
        return data


def auth():
    pass


def get_messages():
    pass


if __name__ == '__main__':
    # client = TelegramApi()
    client.get_chats()
