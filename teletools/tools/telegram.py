from time import sleep

from ..classes.chat import Chat
from ..classes.message import Message
from telethon import TelegramClient, events
from pprint import pprint
from .database import Database
from collections import deque
from threading import Thread
import asyncio


class TelegramApi:
    def __init__(self, api_id, api_hash, loop):
        self.loop = loop  # asyncio loop
        self.database = Database()

        # support updating
        self.new_data = False
        self.updated = set()

        self.client = TelegramClient('session', api_id, api_hash)
        self.client.start()
        # self.update_dialogs()

        # using decorators
        self.client.on(events.NewMessage())(self.new_message_handler)
        self.client.on(events.MessageEdited())(self.edit_message_handler)
        self.client.on(events.MessageRead())(self.read_message_handler)

        # updating data before start
        self.loop.create_task(self.client.catch_up())
        self.loop.create_task(self.update_dialogs())

        # starting real time updates
        self.loop.create_task(self.run_until_disconnected())

    async def run_until_disconnected(self):
        await self.client.disconnected

    async def update_dialogs(self):
        dialogs = await self.client.get_dialogs()
        self.database.update_dialogs(dialogs)

        self.new_data = True

    def get_dialogs(self, archived=False):
        dialogs = self.database.get_dialogs(archived=archived)
        self.new_data = False
        return dialogs

    async def update_messages(self, id, limit, min_id=None, max_id=None):
        messages = await self.client.get_messages(id, limit=limit)

        for message in messages:
            message.from_username, message.from_name = await self._get_message_name(message)

        self.database.update_messages(messages, id)
        self.new_data = True

    def que_update_messages(self, id, limit, min_id=None, max_id=None):
        self.loop.create_task(self.update_messages(id, limit, min_id, max_id))

    def get_messages(self, id, limit=30, min_id=None, max_id=None):
        # TODO implement min_id, max_id
        self.first_update(id)
        messages = self.database.get_messages(dialog_id=id, limit=limit, min_id=min_id, max_id=max_id)
        if len(messages) != limit:
            self.que_update_messages(id, limit, min_id, max_id)
        self.new_data = False
        return messages

    def first_update(self, id, limit=100):
        if id not in self.updated:
            self.que_update_messages(id, limit=limit)
            self.updated.add(id)

    async def _get_message_name(self, message_obj):
        if message_obj.from_id:
            username, name = self.database.get_user_name(message_obj.from_id)
            if username:
                return username, name

            else:
                user = await self.client.get_entity(message_obj.from_id)
                self.database.update_user(user)
                username = user.username
                name = (user.first_name if user.first_name else '') + (
                    ' ' if user.first_name else '') + (user.last_name if user.last_name else '')
                return username, name
        else:
            return None, None

    async def new_message_handler(self, event):
        message = event.message
        dialog = await event.get_chat()

        message.from_username, message.from_name = await self._get_message_name(message)

        self.database.update_messages(message, dialog.id)
        self.database.update_dialogs(dialog)
        self.new_data = True

    async def edit_message_handler(self, event):
        message = event.message
        dialog = await event.get_chat()

        message.from_username, message.from_name = await self._get_message_name(message)

        self.database.update_messages(message, dialog.id)
        self.database.update_dialogs(dialog)
        self.new_data = True

    async def read_message_handler(self, event):
        messages = await event.get_messages()
        dialog = await event.get_chat()

        for message in messages:
            message.from_username, message.from_name = await self._get_message_name(message)

        self.database.update_messages(messages, dialog.id)
        self.database.update_dialogs(dialog)
        self.new_data = True
