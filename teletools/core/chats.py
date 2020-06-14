from time import sleep


class Chats:
    def __init__(self, window):
        self.window = window
        self.active_chat = None
        self.chat_list = None
        self.height, self.width = self.window.getmaxyx()


    def set_chat_list(self, chat_list):
        self.chat_list = chat_list
        if self.active_chat is None:
            self.active_chat = self.chat_list[0]

        self.window.erase()
        for line, chat in enumerate(self.chat_list):
            self.window.insstr(line, 0, chat.name)

        self.window.refresh()
        sleep(2)
        self.window.scroll(2)
        self.window.refresh()
        sleep(2)



