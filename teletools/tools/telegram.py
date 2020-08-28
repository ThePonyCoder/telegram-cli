import asyncio
import queue
import threading
import time
import os.path

from telethon import TelegramClient, events

from .database import Database
from ..classes.update import UpdateType

AUTODOWNLOAD_PHOTOS = False


class TelegramApi:
    def __init__(self, api_id, api_hash, new_data_event: threading.Event, update_queue: queue.Queue):
        self.loop = asyncio.get_event_loop()  # asyncio loop
        self.database = Database()

        # support updating
        self.last_update = {}
        self.updated = set()
        self.new_data_event = new_data_event
        self.update_queue = update_queue

        self.client = TelegramClient('session', api_id, api_hash)
        self.client.start()

        # using decorators
        self.client.on(events.NewMessage())(self._new_message_handler)
        self.client.on(events.MessageEdited())(self._edit_message_handler)
        self.client.on(events.MessageRead())(self._read_message_handler)

        # updating data before start
        self.loop.create_task(self._update_dialogs())

        # starting real time updates
        self.loop.create_task(self._run_until_disconnected())

        # starting updates_handler
        self.loop.create_task(self._updates_handler())

    async def _run_until_disconnected(self):
        await self.client.disconnected

    async def _updates_handler(self):
        """Main loop function"""
        while True:
            if not self.update_queue.empty():
                # print('FOND NEW TASK IN QUEUE, WORKING...')
                update = self.update_queue.get()
                if update.type == UpdateType.DIALOGUES_UPDATE and \
                        (time.time() - self.last_update.get('dialogs', 0)) > 120:
                    # TODO: make setting for timeout
                    self.loop.create_task(self._update_dialogs())
                    self.last_update['dialogs'] = time.time()
                if update.type == UpdateType.MESSAGES_UPDATE and \
                        (time.time() - self.last_update.get(update.dialog_id, 0)) > 120:
                    self.loop.create_task(self._update_messages(id=update.dialog_id,
                                                                ids=update.ids))
                if update.type == UpdateType.MEDIA_DOWNLOAD:
                    # print('CREATING DOWNLOAD_MEDIA_TASK_IN_LOOP')
                    self.loop.create_task(
                        self._download_media(dialog_id=update.dialog_id,
                                             message_id=update.message_id,
                                             download_handler=update.download_handler)
                    )
                if update.type == UpdateType.SEND_MESSAGE:
                    self.loop.create_task(
                        self._send_message(
                            dialog_id=update.dialog_id,
                            text=update.message
                        )
                    )

            else:
                await asyncio.sleep(5)
            # await asyncio.sleep(0.1)

    async def _update_dialogs(self):
        dialogs = await self.client.get_dialogs()
        self.database.update_dialogs(dialogs)

        self.new_data_event.set()

    async def _update_messages(self, id, limit=10, min_id=None, max_id=None, ids=None):
        # TODO: settings for default limits
        messages = await self.client.get_messages(id, limit=limit)

        replies_to_merge = []
        for message in messages:
            message.from_username, message.from_name = await self.__get_message_name(message)
            if message.is_reply:
                msg = await self.client.get_messages(id, limit=1, ids=message.reply_to_msg_id)
                if msg:
                    msg.from_username, msg.from_name = await self.__get_message_name(message)
                    replies_to_merge.append(msg)
        messages.extend(replies_to_merge)

        self.database.update_messages(messages, id)
        self.new_data_event.set()

    async def __get_message_name(self, message_obj):
        if message_obj.from_id:
            username, name = self.database.get_user_name(message_obj.from_id)
            if username:
                return username, name

            else:
                user = await self.client.get_entity(message_obj.from_id)
                self.database.update_user(user)
                username = user.username
                name = (user.first_name if user.first_name else '') + \
                       (' ' if user.first_name else '') + \
                       (user.last_name if user.last_name else '')
                return username, name
        else:
            return None, None

    async def _new_message_handler(self, event):
        # print('new_message')
        message = event.message

        dialog = await event.get_chat()

        message.from_username, message.from_name = await self.__get_message_name(message)
        self.database.update_messages(message, dialog.id)

        self.new_data_event.set()

    async def _edit_message_handler(self, event):
        # print('edit_message')
        message = event.message
        dialog = await event.get_chat()

        message.from_username, message.from_name = await self.__get_message_name(message)

        self.database.update_messages(message, dialog.id)
        self.new_data_event.set()

    async def _read_message_handler(self, event):
        # print('read_message')
        pass
        messages = await event.get_messages()
        dialog = await event.get_chat()

        for message in messages:
            message.from_username, message.from_name = await self.__get_message_name(message)

        self.database.update_messages(messages, dialog.id)
        self.new_data_event.set()

    async def _download_media(self, dialog_id, message_id, download_handler=print, auto_open=True):
        message = await self.client.get_messages(dialog_id, ids=message_id)
        file = message.file
        # print(file.mime_type)
        if file is None:
            # print(f'No media in message [id: {message_id}]')
            return

        filename = f'files/{dialog_id}_{message_id}{file.ext}'  # TODO: make settings for download folder
        if not os.path.isfile(filename):
            await message.download_media(filename, progress_callback=download_handler)
        if auto_open:
            if file.mime_type.startswith('image'):
                os.system(f'sxiv {filename}')
            if file.mime_type.startswith('video'):
                os.system(f'mpv {filename}')
        # TODO: support more mime types + setting for default image viewers

    async def _send_message(self, dialog_id, text):
        message = await self.client.send_message(entity=dialog_id, message=text)
        message.from_id = (await self.client.get_me()).id
        message.from_username, message.from_name = await self.__get_message_name(message)
        print(message.from_name)
        self.database.update_messages(message, dialog_id)
        self.new_data_event.set()
