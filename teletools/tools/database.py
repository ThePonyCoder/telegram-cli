import sqlite3
from pprint import pprint


class Database:
    def __init__(self, db_name='db.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

        self.create_tables()

    def update_dialogs(self, dialogs_obj):
        if not isinstance(dialogs_obj, list):
            dialogs_obj = [dialogs_obj]

        for dialog_obj in dialogs_obj:
            self.cursor.execute("""
                DELETE FROM dialogs
                WHERE id = ?
            """, [dialog_obj.id])
            self.cursor.execute("""
                INSERT INTO dialogs
                VALUES (?,?,?,?,?,?,?,?)
            """, [
                dialog_obj.id,
                dialog_obj.pinned,
                dialog_obj.archived,
                dialog_obj.date.timestamp(),
                dialog_obj.name,
                dialog_obj.is_user,
                dialog_obj.is_group,
                dialog_obj.is_channel,
            ])
        self.commit()

    def update_messages(self, messages_obj):
        if not isinstance(messages_obj, list):
            messages_obj = [messages_obj]

        for message_obj in messages_obj:
            to_id = None
            if hasattr(message_obj.to_id, 'user_id'):
                to_id = message_obj.to_id.user_id
            if hasattr(message_obj.to_id, 'chat_id'):
                to_id = message_obj.to_id.chat_id
            if hasattr(message_obj.to_id, 'channel_id'):
                to_id = message_obj.to_id.channel_id

            self.cursor.execute("""
                DELETE FROM messages
                WHERE (to_id,id) = (?,?)
            """, [to_id, message_obj.id])

            self.cursor.execute("""
                INSERT INTO messages
                VALUES (
                    ?,?,?,?,?,
                    ?,?,?,?,?,
                    ?,?,?,?,?,
                    ?,?,?,?,?,
                    ?,?,?,?,?,
                    ?,?,?,?,?,
                    ?,?,?
                )
            """, [
                message_obj.id,
                to_id,
                message_obj.out,
                message_obj.mentioned,
                message_obj.media_unread,
                message_obj.silent,
                message_obj.post,
                message_obj.post_author,
                message_obj.date.timestamp() if message_obj.date else None,
                message_obj.message,
                message_obj.from_id,
                message_obj.via_bot_id,
                message_obj.views,
                message_obj.edit_date.timestamp() if message_obj.edit_date else None,
                message_obj.is_reply,
                message_obj.reply_to_msg_id,
                True if message_obj.forward else False,
                message_obj.forward.original_fwd.from_id if message_obj.forward else None,
                message_obj.forward.original_fwd.from_name if message_obj.forward else None,
                message_obj.forward.original_fwd.channel_id if message_obj.forward else None,
                message_obj.forward.original_fwd.channel_post if message_obj.forward else None,
                message_obj.forward.original_fwd.post_author if message_obj.forward else None,
                True if message_obj.media else False,
                True if message_obj.photo else False,
                True if message_obj.audio else False,
                True if message_obj.voice else False,
                True if message_obj.document else False,
                True if message_obj.video else False,
                True if message_obj.file else False,
                True if message_obj.gif else False,
                True if message_obj.invoice else False,
                True if message_obj.poll else False,
                True if message_obj.sticker else False,
            ])
        self.commit()

    def get_messages(self, chat_id, limit=10, max_id=None, min_id=None):
        cursor = None
        if max_id is None and min_id is None:
            cursor = self.cursor.execute("""
                SELECT * from messages
                WHERE 
                    to_id=?
                ORDER BY 
                    date DESC
                LIMIT ?;
            """, [chat_id, limit])
        messages = []
        for i in cursor:
            message = {
                'id': i[0],
                'to_id': i[1],
                'out': i[2],
                'mentioned': i[3],
                'media_unread': i[4],
                'silent': i[5],
                'post': i[6],
                'post_author': i[7],
                'date': i[8],
                'message': i[9],
                'from_id': i[10],
                'via_bot_id': i[11],
                'views': i[12],
                'edit_date': i[13],

                'is_reply': i[14],
                'reply_to_msg_id': i[15],

                'forward': i[16],
                'forward_from_id': i[17],
                'forward_from_name': i[18],
                'forward_channel_id': i[19],
                'forward_channel_post': i[20],
                'forward_post_author': i[21],

                'media': i[22],
                'photo': i[23],
                'audio': i[24],
                'voice': i[25],
                'document': i[26],
                'video': i[27],
                'file': i[28],
                'gif': i[29],
                'invoice': i[30],
                'poll': i[31],
                'sticker': i[32]
            }
            messages.append(message)
        return messages

    def get_dialogs(self, archived=False):
        # TODO execute by achived bool
        if archived is False:
            dialogs_list = self.cursor.execute("""
                SELECT * from dialogs
                WHERE
                    archived=0
                ORDER BY 
                    date DESC
            """).fetchall()
        else:
            dialogs_list = self.cursor.execute("""
                SELECT * from dialogs
                WHERE
                    archived=1
                ORDER BY 
                    date DESC
            """).fetchall()

        dialogs = {}
        for i in dialogs_list:
            dialog = {
                'id': i[0],
                'pinned': i[1],
                'archived': i[2],
                'date': i[3],
                'name': i[4],
                'is_user': i[5],
                'is_group': i[6],
                'is_channel': i[7]
            }

    def get_dialog_name(self, id):
        return self.cursor.execute("""
            SELECT name from dialogs
            WHERE 
                id=?
        """, [id]).fetchall()[0]

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS dialogs(
                id INTEGER UNIQUE,
                pinned INTEGER,
                archived INTEGER,
                date INTEGER,
                name TEXT,
                is_user INTEGER,
                is_group INTEGER,
                is_channel INTEGER                
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER,
                to_id INTEGER,
                out INTEGER,
                mentioned INTEGER,
                media_unread INTEGER,
                silent INTEGER,
                post INTEGER,
                post_author INTEGER,
                date INTEGER,
                message TEXT,
                from_id INTEGER,
                via_bot_id INTEGER,
                views INTEGER,
                edit_date INTEGER,
                
                
                is_reply INTEGER,
                reply_to_msg_id INTEGER,
                
                forward INTEGER,
                forward_from_id INTEGER,
                forward_from_name TEXT,
                forward_channel_id INTEGER,
                forward_channel_post INTEGER,
                forward_post_author TEXT,
                
                
                media INTEGER,
                photo INTEGER,
                audio INTEGER,
                voice INTEGER,
                document INTEGER,
                video INTEGER,
                file INTEGER,
                gif INTEGER,
                invoice INTEGER,
                poll INTEGER,
                sticker INTEGER                                                  
            );
        """)
        self.commit()

    def commit(self):
        self.conn.commit()


if __name__ == '__main__':
    from telethon import events, TelegramClient

    client = TelegramClient('session', )  # token huoken)


    async def main():
        dialogs = await client.get_dialogs()
        return dialogs

        # client.start()


    async def get_messages(dialogs):
        _messages = await client.get_messages(dialogs, limit=30)
        return _messages


    # with client:
    #     dialogs = client.loop.run_until_complete(main())
    #     messages = client.loop.run_until_complete(get_messages(dialogs[0].id))
    db = Database()
    # db.update_dialogs(dialogs)
    # db.update_messages(messages)
    pprint(db.get_messages(1123575655))

    # print(dialogs[0].date.timestamp())
