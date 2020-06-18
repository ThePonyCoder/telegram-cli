from time import sleep

from ..classes.chat import Chat
from ..classes.message import Message
from telethon import TelegramClient, events
from pprint import pprint
from .database import Database
from collections import deque
from threading import Thread


class TelegramApi:
    def __init__(self, api_id, api_hash):
        self.database = Database()

        # support updating
        self.new_data = False

        self.client = TelegramClient('session', api_id, api_hash)
        self.client.start()
        # self.update_dialogs()

        # using decorators
        self.client.on(events.NewMessage())(self.new_message_handler)
        self.client.on(events.MessageEdited())(self.edit_message_handler)
        self.client.on(events.MessageRead())(self.read_message_handler)

        # updating data before start
        self.client.loop.create_task(self.client.catch_up())
        self.que_update_dialogs()

        # starting main loop thread
        Thread(target=self.client.run_until_disconnected).start()

    async def update_dialogs(self):
        dialogs = await self.client.get_dialogs()
        self.database.update_dialogs(dialogs)

        self.new_data = True

    def que_update_dialogs(self):
        self.client.loop.create_task(self.update_dialogs())

    def get_dialogs(self, archived=False):
        dialogs = self.database.get_dialogs(archived=archived)
        self.new_data = False
        return dialogs

    async def update_messages(self, id, limit, min_id=None, max_id=None):
        messages = await self.client.get_messages(id, limit=limit, min_id=min_id, max_id=max_id)
        self.database.update_messages(messages)
        self.new_data = True

    def que_update_messages(self, id, limit, min_id=None, max_id=None):
        self.client.loop.create_task(self.update_messages(id, limit, min_id, max_id))

    def get_messages(self, id, limit, min_id=None, max_id=None):
        # TODO implement min_id, max_id
        messages = self.database.get_messages(chat_id=id, limit=limit, min_id=min_id, max_id=max_id)
        if len(messages) != limit:
            self.que_update_messages()
        self.new_data = False
        return messages

    async def new_message_handler(self, event):
        message = event.message
        dialog = await event.get_chat()
        self.database.update_messages(message)
        self.database.update_dialogs(dialog)
        self.new_data = True

    async def edit_message_handler(self, event):
        message = event.message
        dialog = await event.get_chat()
        self.database.update_messages(message)
        self.database.update_dialogs(dialog)
        self.new_data = True

    async def read_message_handler(self, event):
        messages = await event.get_messages()
        dialog = await event.get_chat()
        self.database.update_messages(messages)
        self.database.update_dialogs(dialog)
        self.new_data = True
