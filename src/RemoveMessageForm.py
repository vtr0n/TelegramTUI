import curses
from src.telegramApi import client
from src import npyscreen


class RemoveMessageForm(npyscreen.ActionForm):

    def create(self):
        y, x = self.parentApp.MainForm.useable_space()
        self.show_atx = x // 2 - 10
        self.show_aty = y // 2 - 5

        self.name = "Delete Message?"
        new_handlers = {
            # exit
            "^Q": self.exit_func,
            155: self.exit_func,
            curses.ascii.ESC: self.exit_func
        }
        self.add_handlers(new_handlers)

        self.display()

    def on_ok(self):
        current_message = self.parentApp.MainForm.messageBoxObj.entry_widget.cursor_line
        current_user = self.parentApp.MainForm.chatBoxObj.value
        messages = self.parentApp.MainForm.messageBoxObj.get_messages_info(current_user)

        message_id = messages[-current_message - 1].id

        client.delete_message(current_user, message_id)

        new_data = []
        for i in range(len(client.messages[current_user])):
            if client.messages[current_user][i].id != message_id:
                new_data.append(client.messages[current_user][i])

        client.messages[current_user] = new_data

        self.parentApp.MainForm.messageBoxObj.update_messages(current_user)
        self.parentApp.MainForm.messageBoxObj.display()
        self.parentApp.switchForm("MAIN")

    def on_cancel(self):
        self.parentApp.switchForm("MAIN")

    def exit_func(self, _input):
        exit(0)
