import curses
from src.telegramApi import client
from src import npyscreen


class ForwardMessage(npyscreen.BoxTitle):

    def create(self):
        data = []
        for i in range(len(client.dialogs)):
            data.append(client.dialogs[i].name)

        self.values = data

    def when_value_edited(self):
        if self.value is not None:
            current_message = self.parent.parentApp.MainForm.messageBoxObj.entry_widget.cursor_line
            current_user = self.parent.parentApp.MainForm.chatBoxObj.value
            messages = self.parent.parentApp.MainForm.messageBoxObj.get_messages_info(current_user)

            message_id = messages[-current_message - 1].id
            message_text = self.parent.parentApp.MainForm.inputBoxObj.value

            reply_user = self.value

            client.message_send(message_text, reply_user, message_id)


class ForwardMessageForm(npyscreen.ActionForm):

    def create(self):
        self.name = "Forward Message"
        new_handlers = {
            # exit
            "^Q": self.exit_func,
            155: self.exit_func,
            curses.ascii.ESC: self.exit_func
        }
        self.add_handlers(new_handlers)

        fwd = self.add(ForwardMessage, name="Select User")
        fwd.create()

    def on_ok(self):
        self.parentApp.switchForm("MAIN")

    def on_cancel(self):
        self.parentApp.switchForm("MAIN")

    def exit_func(self, _input):
        exit(0)
