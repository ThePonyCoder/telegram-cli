import sqlite3
from pprint import pprint


class Database:
    def __init__(self, db_name='db.db'):
        self.db_name = db_name

        # self.conn = None
        # cursor = None

        # creating default tables
        self.create_tables()

    def connect(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        return conn, cursor

    def update_dialogs(self, dialogs_obj):
        conn, cursor = self.connect()
        if not isinstance(dialogs_obj, list):
            dialogs_obj = [dialogs_obj]

        for dialog_obj in dialogs_obj:
            cursor.execute("""
                DELETE FROM dialogs
                WHERE id = ?
            """, [dialog_obj.id])
            cursor.execute("""
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
        conn.commit()
        conn.close()

    def update_dialog_time(self, messages_obj, dialog_id):
        bst = 0
        for message in messages_obj:
            if message.date:
                bst = max(bst, message.date.timestamp())
        conn, cursor = self.connect()
        time = cursor.execute("""
            SELECT 
                date 
            FROM 
                dialogs
            WHERE
                id=?
        """, [dialog_id]).fetchall()[0][0]
        if time < bst:
            cursor.execute("""
                UPDATE
                    dialogs
                SET
                    date=?
                WHERE
                    id=?
            """, [bst, dialog_id])
        conn.commit()
        conn.close()

    def update_messages(self, messages_obj, dialog_id):
        # TODO: change dialog update time
        if not isinstance(messages_obj, list):
            messages_obj = [messages_obj]

        self.update_dialog_time(messages_obj, dialog_id)  # updating dialog update_time

        conn, cursor = self.connect()

        for message_obj in messages_obj:
            if not message_obj.from_name:
                message_obj.from_name = self.get_dialog_name(dialog_id)
            to_id = None
            if hasattr(message_obj.to_id, 'user_id'):
                to_id = message_obj.to_id.user_id
            if hasattr(message_obj.to_id, 'chat_id'):
                to_id = message_obj.to_id.chat_id * -1
            if hasattr(message_obj.to_id, 'channel_id'):
                to_id = int('-100' + str(message_obj.to_id.channel_id))

            cursor.execute("""
                DELETE FROM messages
                WHERE (dialog_id,id) = (?,?)
            """, [dialog_id, message_obj.id])

            cursor.execute("""
                INSERT INTO messages
                VALUES (
                    ?,?,?,?,?,
                    ?,?,?,?,?,
                    ?,?,?,?,?,
                    ?,?,?,?,?,
                    ?,?,?,?,?,
                    ?,?,?,?,?,
                    ?,?,?,?,?,
                    ?
                )
            """, [
                message_obj.id,
                dialog_id,
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
                to_id,
                str(message_obj.from_name),
                str(message_obj.from_username)
            ])
        conn.commit()
        conn.close()

    def get_messages(self, dialog_id, limit=10, max_id=None, min_id=None):

        conn, cursor = self.connect()
        if max_id is None and min_id is None:
            cursor = cursor.execute("""
                SELECT * from messages
                WHERE 
                    dialog_id=?
                ORDER BY 
                    date DESC
                LIMIT ?;
            """, [dialog_id, limit])
        messages = []
        for i in cursor:
            message = {
                'id': i[0],
                'dialog_id': i[1],
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
                'sticker': i[32],
                'to_id': i[33],
                'from_name': i[34],
                'from_username': i[35]
            }
            messages.append(message)
        conn.commit()
        conn.close()
        return messages

    def get_dialogs(self, archived=False):
        if archived:
            archived = 1
        else:
            archived = 0

        conn, cursor = self.connect()
        # TODO execute by archived bool

        dialogs_list = cursor.execute("""
            SELECT * from dialogs
            WHERE
                archived=?
            ORDER BY 
                pinned DESC, date DESC
        """, [archived]).fetchall()

        dialogs = []
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
            dialogs.append(dialog)
        conn.commit()
        conn.close()
        return dialogs

    def get_dialog_name(self, id):

        conn, cursor = self.connect()
        name = cursor.execute("""
            SELECT name from dialogs
            WHERE 
                id=?
        """, [id]).fetchall()[0][0]
        conn.commit()
        conn.close()
        return name

    def update_user(self, user):
        conn, cursor = self.connect()
        cursor.execute("""
            DELETE FROM 
                users
            WHERE 
                id=?
        """, [user.id])

        cursor.execute("""
            INSERT INTO 
                users
            VALUES 
                (?,?,?)
        """, [user.id,
              (user.first_name if user.first_name else '')
              + (' ' if user.first_name else '')
              + (user.last_name if user.last_name else ''),
              user.username])
        conn.commit()
        conn.close()

    def get_user_name(self, id):
        """
        :param id: user_id
        :return: [username, name] if exist or [None,None]
        """
        conn, cursor = self.connect()
        rows = cursor.execute("""
            SELECT 
                name, username 
            FROM 
                users
            WHERE
                id=?
                
        """, [id]).fetchall()
        conn.close()
        if rows:
            name, username = rows[0]
        else:
            username, name = None, None
        return username, name

    def create_tables(self):

        conn, cursor = self.connect()
        cursor.execute("""
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER,
                dialog_id INTEGER,
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
                sticker INTEGER,    
                
                to_id INTEGER,  
                from_name TEXT,
                from_username TEXT                            
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER,
                name TEXT,
                username TEXT         
            );
        """)
        conn.commit()
        conn.close()


if __name__ == '__main__':
    from telethon import events, TelegramClient

    with open('auth.txt', 'r') as f:
        api_id = f.readline().strip()
        api_hash = f.readline().strip()
        client = TelegramClient('session', api_id, api_hash)  # token huoken)
        client.start()


    async def main():
        dialogs = await client.get_dialogs()
        for dia in dialogs:
            messages = await client.get_messages(dia.id, limit=30)
            print(messages[3].to_id, dia.id)


    client.loop.run_until_complete(main())

    # pprint(db.get_messages(1123575655))

    # print(dialogs[0].date.timestamp())
