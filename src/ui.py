
import textwrap
import curses
import configparser
import os.path
from datetime import timedelta
from PIL import Image
from src.telegramApi import client
from src import aalib
from src import npyscreen

class ChatBox(npyscreen.BoxTitle):

    def when_value_edited(self):
        # event to change message dialog box
        self.parent.parentApp.queue_event(npyscreen.Event("event_chat_select"))


class MessageBox(npyscreen.BoxTitle):

    def when_value_edited(self):
        pass

    def when_cursor_moved(self):
        self.parent.parentApp.queue_event(npyscreen.Event("event_messagebox_change_cursor"))


class InputBox(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLineEdit


class MainForm(npyscreen.FormBaseNew):

    def create(self):
        # Events
        self.add_event_hander("event_chat_select", self.event_chat_select)
        self.add_event_hander("event_inputbox_send", self.message_send)
        self.add_event_hander("event_messagebox_change_cursor", self.event_messagebox_change_cursor)

        # import config settings
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.emoji = True if config.get('other', 'emoji') == "True" else False
        self.aalib = True if config.get('other', 'aalib') == "True" else False
        self.timezone = int(config.get('other', 'timezone'))
        self.app_name = config.get('app', 'name')

        # window size
        y, x = self.useable_space()
        self.y, self.x = y, x

        # create ui form
        self.chatBoxObj = self.add(ChatBox, name="Chats", value=0, relx=1, max_width=x // 5, rely=2, max_height=-5,
                                   values="")

        self.messageBoxObj = self.add(MessageBox, name="", rely=2,
                                      relx=(x // 5) + 1, max_height=-5, editable=True,
                                      custom_highlighting=True, highlighting_arr_color_data=[0])

        self.otherBoxObj = self.add(ChatBox, name="Other", value=0, relx=1, max_width=x // 5, max_height=-5, )
        self.otherBoxObj.values = ["🕮  Contacts"] if self.emoji else ["Contacts"]

        self.inputBoxObj = self.add(InputBox, name="Input", relx=(x // 5) + 1, rely=-7)

        # init buffer
        self.buff_messages = len(client.dialogs) * [None]

        # inti handlers
        new_handlers = {
            # exit
            "^Q": self.exit_func,
            155: self.exit_func,
            curses.ascii.ESC: self.exit_func,
            # send message
            "^S": self.message_send,
            138: self.message_send
        }
        self.add_handlers(new_handlers)

        # fill first data
        self.update_messages()
        self.update_chat()

    def update_messages(self):
        current_user = self.chatBoxObj.value
        messages = self.get_messages_info()

        color_data = []
        data = []
        for i in range(len(messages) - 1, -1, -1):
            data.append(messages[i].name + " " + messages[i].message)
            color_data.append(messages[i].color)

        self.messageBoxObj.entry_widget.highlighting_arr_color_data = color_data

        self.messageBoxObj.values = data

        if len(messages) > self.y - 12:
            self.messageBoxObj.entry_widget.start_display_at = len(messages) + 12 - self.y
        else:
            self.messageBoxObj.entry_widget.start_display_at = 0

        self.messageBoxObj.entry_widget.cursor_line = len(messages)

        self.messageBoxObj.name = client.dialogs[current_user].name
        self.messageBoxObj.footer = client.online[current_user]

        self.messageBoxObj.display()

    def update_chat(self):
        current_user = self.chatBoxObj.value
        unread = 0

        color_new_message = self.theme_manager.findPair(self, 'DANGER')
        color_online = self.theme_manager.findPair(self, 'IMPORTANT')
        color_data = []

        data = []
        for i in range(len(client.dialogs)):
            special = ""
            if hasattr(client.dialogs[i].dialog.peer, 'user_id'):
                special = "👤 " if not client.dialogs[i].entity.bot else "🤖 "
            elif hasattr(client.dialogs[i].dialog.peer, 'channel_id'):
                special = "📢 "
            elif hasattr(client.dialogs[i].dialog.peer, 'chat_id'):
                special = "👥 "

            if not self.emoji:
                special = ""
            unread += int(client.dialogs[i].unread_count)

            highlight = []
            if client.online[i] == "Online":
                for j in range(len(client.dialogs[i].name)):
                    highlight.append(color_online)

            if client.dialogs[i].unread_count != 0 and i != current_user:
                data.append(special + client.dialogs[i].name + "[" + str(client.dialogs[i].unread_count) + "]")
                color_data.append([color_new_message, color_new_message])
                color_data[i].extend(highlight)
            else:
                data.append(special + client.dialogs[i].name)
                color_data.append([0, 0])
                color_data[i].extend(highlight)

        # come up with a feature about mute messages
        if unread != 0:
            self.name = self.app_name + " " + "[" + str(unread) + "]"
        else:
            self.name = self.app_name
        # self.display()

        self.chatBoxObj.values = data
        self.chatBoxObj.entry_widget.custom_highlighting = True
        self.chatBoxObj.entry_widget.highlighting_arr_color_data = color_data
        self.chatBoxObj.display()

    def get_messages_info(self):
        current_user = self.chatBoxObj.value
        messages = client.get_messages(current_user)

        # check buffer
        buff = self.buff_messages[current_user]
        if buff is not None and messages is not None and \
                len(buff) != 0 and len(messages) != 0 and \
                buff[0].id == messages[0].id:
            return buff

        # structure for the dictionary
        class user_info:
            def __init__(self, color, name):
                self.color = color
                self.name = name

        users = {}
        max_name_len = 0

        # 1 - dialog with user
        if hasattr(client.dialogs[current_user].dialog.peer, 'user_id'):
            dialog_type = 1
            # set interlocutor
            name = client.dialogs[current_user].name if hasattr(client.dialogs[current_user], 'name') else \
                client.dialogs[current_user].first_name
            users[client.dialogs[current_user].dialog.peer.user_id] = user_info(
                self.theme_manager.findPair(self, 'WARNING'), name)

            # set me
            name = client.me.first_name if hasattr(client.me, 'first_name') else client.me.last_name
            users[client.me.id] = user_info(self.theme_manager.findPair(self, 'NO_EDIT'), name)

            max_name_len = max(len(users[client.dialogs[current_user].dialog.peer.user_id].name),
                               len(users[client.me.id].name))

        # 2 - chat group
        elif hasattr(client.dialogs[current_user].dialog.peer, 'chat_id'):
            dialog_type = 2
            max_name_len = 0
            for i in range(len(messages)):
                username = ""
                if messages[i].sender is None:
                    username = "Unknown"
                elif hasattr(messages[i].sender, 'first_name') and messages[i].sender.first_name is not None:
                    username = messages[i].sender.first_name
                elif hasattr(messages[i].sender, 'last_name') and messages[i].sender.last_name is not None:
                    username = messages[i].sender.last_name

                users[messages[i].sender.id] = user_info(
                    self.theme_manager.findPair(self, 'WARNING'), username)

                max_name_len = max(max_name_len, len(username))

            # set me
            name = client.me.first_name if hasattr(client.me, 'first_name') else client.me.last_name
            users[client.me.id] = user_info(self.theme_manager.findPair(self, 'NO_EDIT'), name)

        # 3 - channel
        elif hasattr(client.dialogs[current_user].dialog.peer, 'channel_id'):
            dialog_type = 3

        # -1 not define
        else:
            dialog_type = -1

        class Messages:
            def __init__(self, name, date, color, message, id, read):
                self.name = name
                self.date = date
                self.color = color
                self.message = message
                self.id = id
                self.read = read

        max_read_mess = client.dialogs[current_user].dialog.read_outbox_max_id

        out = []
        for i in range(len(messages)):
            date = messages[i].date
            mess_id = messages[i].id

            if self.emoji:
                if max_read_mess < mess_id and messages[i].out:
                    read = "⚫ "
                else:
                    read = "  "
            else:
                if max_read_mess < mess_id and messages[i].out:
                    read = "* "
                else:
                    read = "  "

            if dialog_type == 1 or dialog_type == 2:
                offset = " " * (max_name_len - (len(users[messages[i].sender.id].name)))
                name = read + users[messages[i].sender.id].name + ":" + offset
                color = (len(read) + len(users[messages[i].sender.id].name)) * [users[messages[i].sender.id].color]

            elif dialog_type == 3:
                name = client.dialogs[current_user].name + ": "
                color = len(name) * [self.theme_manager.findPair(self, 'WARNING')]

            else:
                name = ""
                color = [0]

            media = messages[i].media if hasattr(messages[i], 'media') else None
            mess = messages[i].message if hasattr(messages[i], 'message') \
                                          and isinstance(messages[i].message, str) else None

            if self.aalib and media is not None:
                # if file is not exist
                if hasattr(media, 'photo'):
                    if not os.path.isfile(os.getcwd() + "/downloads/" + str(media.photo.id) + ".jpg"):
                        # download picture
                        client.download_media(media, "downloads/" + str(media.photo.id))

                    max_width = int((self.x - (self.x // 5) - len(name) - 11) / 1.3)
                    max_height = int((self.y - 12) / 1.3)

                    screen = aalib.AsciiScreen(width=max_width, height=max_height)
                    image = Image.open(os.getcwd() + "/downloads/" + str(media.photo.id) + ".jpg").convert('L').resize(
                        screen.virtual_size)
                    screen.put_image((0, 0), image)
                    image_text = screen.render()

                    image_text = image_text.split("\n")
                    for k in range(len(image_text) - 1, 0, -1):
                        out.append(Messages(len(name) * " ", date, color, image_text[k], mess_id, read))
                    out.append(Messages(name, date, color, image_text[0], mess_id, read))

            if mess is not None and mess != "":
                if mess.find("\n") == -1:
                    if len(mess) + len(name) + len(read) > self.x - (self.x // 5) - 10:
                        max_char = self.x - (self.x // 5) - len(name) - 10
                        arr = textwrap.wrap(mess, max_char)

                        for k in range(len(arr) - 1, 0, -1):
                            out.append(Messages(len(name) * " ", date, color, arr[k], mess_id, read))

                        out.append(Messages(name, date, color, arr[0], mess_id, read))
                    else:
                        out.append(Messages(name, date, color, mess, mess_id, read))
                else:
                    mess = mess.split("\n")
                    for j in range(len(mess) - 1, 0, -1):
                        if len(mess[j]) + len(name) + len(read) > self.x - (self.x // 5) - 10:
                            max_char = self.x - (self.x // 5) - len(name) - 10
                            arr = textwrap.wrap(mess[j], max_char)

                            for k in range(len(arr) - 1, -1, -1):
                                out.append(Messages(len(name) * " ", date, color, arr[k], mess_id, read))
                        else:
                            out.append(Messages(len(name) * " ", date, color, mess[j], mess_id, read))

                    if len(mess[0]) + len(name) + len(read) > self.x - (self.x // 5) - 10:
                        max_char = self.x - (self.x // 5) - len(name) - 10
                        arr = textwrap.wrap(mess[0], max_char)

                        for k in range(len(arr) - 1, 0, -1):
                            out.append(Messages(len(name) * " ", date, color, arr[k], mess_id, read))

                        out.append(Messages(name, date, color, arr[0], mess_id, read))
                    else:
                        out.append(Messages(name, date, color, mess[0], mess_id, read))

        self.buff_messages[current_user] = out
        return out

    # events
    def event_chat_select(self, event):
        current_user = self.chatBoxObj.value
        client.dialogs[current_user].unread_count = 0

        self.update_chat()
        self.update_messages()

        client.read_all_messages(current_user)

    def event_messagebox_change_cursor(self, event):
        messages = self.get_messages_info()
        date = messages[len(messages) - 1 - self.messageBoxObj.entry_widget.cursor_line].date

        self.messageBoxObj.footer = str(date + (timedelta(self.timezone) // 24))
        self.messageBoxObj.update()

    # handling methods
    def message_send(self, event):
        current_user = self.chatBoxObj.value
        message = self.inputBoxObj.value
        client.message_send(message, current_user)
        self.update_messages()

        self.inputBoxObj.value = ""
        self.inputBoxObj.display()

    def exit_func(self, _input):
        exit(0)

    # update loop
    def while_waiting(self):
        current_user = self.chatBoxObj.value

        if client.need_update_message:
            if client.need_update_current_user == current_user:
                self.update_messages()
                client.read_all_messages(current_user)
                client.dialogs[current_user].unread_count = 0

            self.update_chat()
            client.need_update_message = 0
            client.need_update_current_user = -1

        if client.need_update_online:
            if client.need_update_current_user == current_user:
                self.update_messages()
            self.update_chat()
            client.need_update_current_user = -1
            client.need_update_online = 0

        if client.need_update_read_messages:
            if client.need_update_current_user == current_user:
                self.update_messages()
            client.need_update_current_user = -1
            client.need_update_read_messages = 0


class ContactsForm(npyscreen.FormBaseNew):

    def create(self):
        pass


class App(npyscreen.StandardApp):

    def onStart(self):
        self.addForm("MAIN", MainForm)
        self.addForm("CONTACTS", ContactsForm)
