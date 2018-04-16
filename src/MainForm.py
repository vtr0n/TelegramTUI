import curses
import configparser
from datetime import timedelta
from src.telegramApi import client
from src import npyscreen
from src import chatBox
from src import messageBox
from src import inputBox
from src import functionalBox


class MainForm(npyscreen.FormBaseNew):

    def create(self):
        # Events
        self.add_event_hander("event_chat_select", self.event_chat_select)
        self.add_event_hander("event_inputbox_send", self.message_send)
        self.add_event_hander("event_messagebox_change_cursor", self.event_messagebox_change_cursor)
        self.add_event_hander("event_update_main_form", self.event_update_main_form)

        # import config settings
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.emoji = True if config.get('other', 'emoji') == "True" else False
        self.aalib = True if config.get('other', 'aalib') == "True" else False
        self.timezone = int(config.get('other', 'timezone'))
        self.app_name = config.get('app', 'name')

        # window size
        y, x = self.useable_space()

        # create ui form
        self.chatBoxObj = self.add(chatBox.ChatBox, name="Chats", value=0, relx=1, max_width=x // 5, rely=2,
                                   max_height=-5)
        self.chatBoxObj.create(emoji=self.emoji)

        self.messageBoxObj = self.add(messageBox.MessageBox, rely=2, relx=(x // 5) + 1, max_height=-5, editable=True,
                                      custom_highlighting=True, highlighting_arr_color_data=[0])
        self.messageBoxObj.create(emoji=self.emoji, aalib=self.aalib)

        self.FunctionalBox = self.add(functionalBox.FunctionalBox, name="Other", value=0, relx=1, max_width=x // 5,
                                      max_height=-5, )
        self.FunctionalBox.values = ["🕮  Contacts"] if self.emoji else ["Contacts"]

        self.inputBoxObj = self.add(inputBox.InputBox, name="Input", relx=(x // 5) + 1, rely=-7)

        # inti handlers
        new_handlers = {
            # exit
            "^Q": self.exit_func,
            155: self.exit_func,
            curses.ascii.ESC: self.exit_func,
            # send message
            "^S": self.message_send,
            curses.ascii.alt(curses.ascii.NL): self.message_send,
            curses.ascii.alt(curses.KEY_ENTER): self.message_send,
            # forward message
            "^F": self.forward_message,
            # delete message
            "^R": self.remove_message,
            # delete message
            "^D": self.download_file,
            # send file
            "^O": self.file_send
        }
        self.add_handlers(new_handlers)

        # fill first data
        self.messageBoxObj.update_messages(0)
        self.chatBoxObj.update_chat()

    # events
    def event_chat_select(self, event):
        current_user = self.chatBoxObj.value
        client.dialogs[current_user].unread_count = 0

        self.chatBoxObj.update_chat()
        self.messageBoxObj.update_messages(current_user)

        client.read_all_messages(current_user)

    def event_messagebox_change_cursor(self, event):
        current_user = self.chatBoxObj.value
        messages = self.messageBoxObj.get_messages_info(current_user)
        date = messages[len(messages) - 1 - self.messageBoxObj.entry_widget.cursor_line].date

        self.messageBoxObj.footer = str(date + (timedelta(self.timezone) // 24))
        self.messageBoxObj.update()

    # handling methods
    def message_send(self, event):
        current_user = self.chatBoxObj.value
        message = self.inputBoxObj.value.strip()
        if message is not "":
            client.message_send(message, current_user)
            self.messageBoxObj.update_messages(current_user)

            self.inputBoxObj.value = ""
            self.inputBoxObj.display()

    def file_send(self, event):
        self.parentApp.switchForm("SEND_FILE")

    def forward_message(self, event):
        pass
        # self.parentApp.switchForm("FORWARD_MESSAGE")

    def remove_message(self, event):
        self.parentApp.switchForm("REMOVE_MESSAGE")

    def download_file(self, event):
        pass

    def event_update_main_form(self, event):
        self.display()
        self.messageBoxObj.display()
        self.chatBoxObj.display()

    def exit_func(self, _input):
        exit(0)

    # update loop
    def while_waiting(self):
        current_user = self.chatBoxObj.value

        client.client.sync_updates()
        if client.need_update_message:
            if client.need_update_current_user == current_user:
                self.messageBoxObj.update_messages(current_user)
                client.read_all_messages(current_user)
                client.dialogs[current_user].unread_count = 0

            self.chatBoxObj.update_chat()
            client.need_update_message = 0
            client.need_update_current_user = -1

        if client.need_update_online:
            if client.need_update_current_user == current_user:
                self.messageBoxObj.update_messages(current_user)
            self.chatBoxObj.update_chat()
            client.need_update_current_user = -1
            client.need_update_online = 0

        if client.need_update_read_messages:
            if client.need_update_current_user == current_user:
                self.messageBoxObj.update_messages(current_user)
            client.need_update_current_user = -1
            client.need_update_read_messages = 0
