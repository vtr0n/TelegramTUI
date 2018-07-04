from src import npyscreen
from src.telegramApi import client
import textwrap
from PIL import Image
import os.path
import platform

if platform.system() != 'Darwin':
    import aalib

class MessageBox(npyscreen.BoxTitle):

    # like a __init__
    def create(self, **kwargs):
        self.emoji = kwargs['emoji'] if 'emoji' in kwargs else False
        self.aalib = kwargs['aalib'] if 'aalib' in kwargs else False

        self.buff_messages = len(client.dialogs) * [None]

    def when_value_edited(self):
        if self.value is not None:
            self.parent.parentApp.getForm("MESSAGE_INFO").update()
            self.parent.parentApp.switchForm("MESSAGE_INFO")

    def when_cursor_moved(self):
        self.parent.parentApp.queue_event(npyscreen.Event("event_messagebox_change_cursor"))

    def update_messages(self, current_user):
        messages = self.get_messages_info(current_user)

        color_data = []
        data = []
        for i in range(len(messages) - 1, -1, -1):
            # replace empty char
            messages[i].message = messages[i].message.replace(chr(8203), '')

            data.append(messages[i].name + " " + messages[i].message)
            color_data.append(messages[i].color)

        self.entry_widget.highlighting_arr_color_data = color_data

        self.values = data

        if len(messages) > self.height - 3:
            self.entry_widget.start_display_at = len(messages) - self.height + 3
        else:
            self.entry_widget.start_display_at = 0

        self.entry_widget.cursor_line = len(messages)

        self.name = client.dialogs[current_user].name
        self.footer = client.online[current_user]

        self.display()

    def get_messages_info(self, current_user):
        messages = client.get_messages(current_user)

        # get user info
        users, dialog_type, max_name_len = self.get_user_info(messages, current_user)
        max_read_mess = client.dialogs[current_user].dialog.read_outbox_max_id

        # # check buffer
        # buff = self.buff_messages[current_user]
        # if buff is not None and messages is not None and \
        #         len(buff) != 0 and len(messages) != 0 and \
        #         len(messages) != len(buff) and \
        #         buff[0].id == messages[0].id and max_read_mess == self.buf_max_read_mess:
        #     return buff

        self.buf_max_read_mess = max_read_mess
        out = []
        for i in range(len(messages)):
            date = messages[i].date
            mess_id = messages[i].id

            if self.emoji:
                read = "⚫ " if max_read_mess < mess_id and messages[i].out else "  "
            else:
                read = "* " if max_read_mess < mess_id and messages[i].out else "  "

            # get name if message is forwarding
            prepare_forward_message = self.prepare_forward_messages(messages[i])

            # if chat or interlocutor
            if dialog_type == 1 or dialog_type == 2:
                user_name = users[messages[i].sender.id].name
                user_name = user_name if prepare_forward_message is False else prepare_forward_message
                if(len(user_name)!=0):
                    user_name = textwrap.wrap(user_name, self.width // 5)[0]
                else:
                    user_name = "Deleted Account"
                offset = " " * (max_name_len - (len(user_name)))
                name = read + user_name + ":" + offset
                color = (len(read) + len(user_name)) * [users[messages[i].sender.id].color]

            # if channel
            elif dialog_type == 3:
                user_name = client.dialogs[current_user].name
                user_name = user_name if prepare_forward_message is False else prepare_forward_message
                user_name = textwrap.wrap(user_name, self.width // 5)[0]

                name = user_name + ": "
                color = len(user_name) * [self.parent.theme_manager.findPair(self, 'WARNING')]

            else:
                name = ""
                color = [0]

            media = messages[i].media if hasattr(messages[i], 'media') else None
            mess = messages[i].message if hasattr(messages[i], 'message') \
                                          and isinstance(messages[i].message, str) else None

            image_name = ""
            if self.aalib and media is not None and hasattr(media, 'photo'):
                image_name = name
                name = len(name) * " "

            # add message to out []
            self.prepare_message(out, mess, name, read, mess_id, color, date)

            # add media to out []
            self.prepare_media(out, media, name, image_name, read, mess_id, color, date)

        # update buffer
        self.buff_messages[current_user] = out

        # return Message obj
        return out

    # get names, colors for names
    def get_user_info(self, messages, current_user):

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
                self.parent.theme_manager.findPair(self, 'WARNING'), name)

            # set me
            name = client.me.first_name if hasattr(client.me, 'first_name') else client.me.last_name
            users[client.me.id] = user_info(self.parent.theme_manager.findPair(self, 'NO_EDIT'), name)

            max_name_len = max(len(users[client.dialogs[current_user].dialog.peer.user_id].name),
                               len(users[client.me.id].name))

        # 2 - chat group
        elif hasattr(client.dialogs[current_user].dialog.peer, 'chat_id'):
            dialog_type = 2
            for i in range(len(messages)):
                username = ""
                if messages[i].sender is None:
                    username = "Unknown"
                elif hasattr(messages[i].sender, 'first_name') and messages[i].sender.first_name is not None:
                    username = messages[i].sender.first_name
                elif hasattr(messages[i].sender, 'last_name') and messages[i].sender.last_name is not None:
                    username = messages[i].sender.last_name

                users[messages[i].sender.id] = user_info(
                    self.parent.theme_manager.findPair(self, 'WARNING'), username)

                max_name_len = max(max_name_len, len(username))

            # set me
            name = client.me.first_name if hasattr(client.me, 'first_name') else client.me.last_name
            users[client.me.id] = user_info(self.parent.theme_manager.findPair(self, 'NO_EDIT'), name)

        # 3 - channel
        elif hasattr(client.dialogs[current_user].dialog.peer, 'channel_id'):
            dialog_type = 3

        # -1 not define
        else:
            dialog_type = -1

        return users, dialog_type, max_name_len

    # set forwarding name if need
    def prepare_forward_messages(self, message):
        user_name = False
        fwd_from = message.fwd_from if hasattr(message, 'fwd_from') else None
        if fwd_from is not None:
            if fwd_from.from_id is not None:
                if hasattr(fwd_from, 'sender'):
                    sender = fwd_from.sender
                    user_name = sender.first_name if hasattr(sender, 'first_name') and \
                                                     sender.first_name is not None else sender.last_name
                    user_name = "Fwd " + user_name
                else:
                    user_name = "Fwd Unknown"

                user_name = "Fwd " + fwd_from.channel.title if hasattr(message, 'fwd_from.channel.title') else "Fwd Unknown"

        return user_name

    # structure for out message
    class Messages:
        def __init__(self, name, date, color, message, id, read):
            self.name = name
            self.date = date
            self.color = color
            self.message = message
            self.id = id
            self.read = read

    # add message to Message structure
    def prepare_message(self, out, mess, name, read, mess_id, color, date):

        # add message to return
        if mess is not None and mess != "":
            if mess.find("\n") == -1:
                if len(mess) + len(name) + len(read) > self.width - 10:
                    max_char = self.width - len(name) - 10
                    arr = textwrap.wrap(mess, max_char)

                    for k in range(len(arr) - 1, 0, -1):
                        out.append(self.Messages(len(name) * " ", date, color, arr[k], mess_id, read))

                    out.append(self.Messages(name, date, color, arr[0], mess_id, read))
                else:
                    out.append(self.Messages(name, date, color, mess, mess_id, read))
            # multiline message
            else:
                mess = mess.split("\n")
                for j in range(len(mess) - 1, 0, -1):
                    if len(mess[j]) + len(name) + len(read) > self.width - 10:
                        max_char = self.width - len(name) - 10
                        arr = textwrap.wrap(mess[j], max_char)

                        for k in range(len(arr) - 1, -1, -1):
                            out.append(self.Messages(len(name) * " ", date, color, arr[k], mess_id, read))
                    else:
                        out.append(self.Messages(len(name) * " ", date, color, mess[j], mess_id, read))

                if len(mess[0]) + len(name) + len(read) > self.width - 10:
                    max_char = self.width - len(name) - 10
                    arr = textwrap.wrap(mess[0], max_char)

                    for k in range(len(arr) - 1, 0, -1):
                        out.append(self.Messages(len(name) * " ", date, color, arr[k], mess_id, read))

                    out.append(self.Messages(name, date, color, arr[0], mess_id, read))
                else:
                    out.append(self.Messages(name, date, color, mess[0], mess_id, read))

    # add media to Message structure
    def prepare_media(self, out, media, name, image_name, read, mess_id, color, date):
        if media is not None:
            if hasattr(media, 'photo') and self.aalib:
                try:
                    if not os.path.isfile(os.getcwd() + "/downloads/" + str(media.photo.id) + ".jpg"):
                        # download picture
                        client.download_media(media, "downloads/" + str(media.photo.id))

                    max_width = int((self.width - len(image_name) - 11) / 1.3)
                    max_height = int((self.height - 12) / 1.3)

                    screen = aalib.AsciiScreen(width=max_width, height=max_height)
                    image = Image.open(os.getcwd() + "/downloads/" + str(media.photo.id) + ".jpg").convert('L').resize(
                        screen.virtual_size)
                    screen.put_image((0, 0), image)
                    image_text = screen.render()

                    image_text = image_text.split("\n")
                    for k in range(len(image_text) - 1, 0, -1):
                        out.append(self.Messages(len(image_name) * " ", date, color, image_text[k], mess_id, read))
                    out.append(self.Messages(image_name, date, color, image_text[0], mess_id, read))
                except:
                    out.append(self.Messages(image_name, date, color, "<Unknown photo>", mess_id, read))

            elif hasattr(media, 'photo') and not self.aalib:
                out.append(self.Messages(name, date, color, "<Image>", mess_id, read))

            elif hasattr(media, 'document'):
                try:
                    # print sticker like a emoji
                    if hasattr(media.document.attributes[1], 'stickerset'):
                        out.append(self.Messages(name, date, color,
                                                 "Sticker: " + media.document.attributes[1].alt, mess_id, read))
                except:
                    out.append(self.Messages(name, date, color, "<Document>", mess_id, read))
