from telegramtui.src import npyscreen
from telegramtui.src.telegramApi import client
import time


class ChatBox(npyscreen.BoxTitle):

    def create(self, **kwargs):
        self.emoji = kwargs['emoji'] if 'emoji' in kwargs else False

    def when_value_edited(self):
        # event to change message dialog box
        self.parent.parentApp.queue_event(npyscreen.Event("event_chat_select"))

    def update_chat(self):
        current_user = self.value
        unread = 0

        color_new_message = self.parent.theme_manager.findPair(self, 'DANGER')
        color_online = self.parent.theme_manager.findPair(self, 'IMPORTANT')
        color_data = []

        data = []
        for i in range(len(client.dialogs)):
            special = ""
            dialog = client.dialogs[i]
            if self.emoji:
                if dialog.is_user:
                    special = "👤 " if not dialog.entity.bot else "🤖 "
                elif dialog.is_channel and not dialog.is_group:
                    special = "📢 "
                elif dialog.is_group:
                    special = "👥 "
            else:
                if dialog.is_user:
                    special = "* " if not dialog.entity.bot else "@ "
                elif dialog.is_channel and not dialog.is_group:
                    special = "# "
                elif dialog.is_group:
                    special = "$ "

            timestamp = int(time.time())

            mute_until = client.dialogs[i].dialog.notify_settings.mute_until
            mute_until = 0 if mute_until is None else int(mute_until)

            if timestamp >= int(mute_until):
                unread += int(client.dialogs[i].unread_count)

            highlight = []
            if client.online[i] == "Online":
                for j in range(len(client.dialogs[i].name)):
                    highlight.append(color_online)

            if client.dialogs[i].unread_count != 0 and i != current_user:
                data.append(special + client.dialogs[i].name + "[" + str(client.dialogs[i].unread_count) + "]")
                color = len(special) * [color_new_message] if timestamp >= mute_until else [0, 0]
                color_data.append(color)
                color_data[i].extend(highlight)
            else:
                data.append(special + client.dialogs[i].name)
                color_data.append([0, 0])
                color_data[i].extend(highlight)

        if unread != 0:
            self.parent.name = self.parent.app_name + " " + "[" + str(unread) + "]"
        else:
            self.parent.name = self.parent.app_name

        self.values = data
        self.entry_widget.custom_highlighting = True
        self.entry_widget.highlighting_arr_color_data = color_data

        # this event update all boxes
        self.parent.parentApp.queue_event(npyscreen.Event("event_update_main_form"))
