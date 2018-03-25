import curses
import os
from src.telegramApi import client
from src import npyscreen


class SendFileForm(npyscreen.ActionForm):

    def create(self):
        self.name = "Upload File (Press TAB)"
        new_handlers = {
            # exit
            "^Q": self.exit_func,
            155: self.exit_func,
            curses.ascii.ESC: self.exit_func
        }
        self.add_handlers(new_handlers)

        self.filename = self.add(npyscreen.TitleFilename, name="Filename:")
        self.status = self.add(npyscreen.Textfield, name="Status:", editable=False)

    def on_ok(self):
        self.status.value = ""
        self.display()

        if os.path.isfile(self.filename.value):
            current_user = self.parentApp.MainForm.chatBoxObj.value
            client.file_send(self.filename.value, current_user, self.download_progress)
            # need change it
            self.parentApp.MainForm.messageBoxObj.update_messages(current_user)

            self.status.value = ""
            self.parentApp.switchForm("MAIN")
        else:
            self.status.value = "File is not exist"
            self.display()

    def download_progress(self, sent_bytes, total):
        name = "Status: "
        status = (sent_bytes * (self.max_x - len(name) - 8)) // total
        status = 1 if status == 0 else status
        self.status.value = name + "-" * status + ">"
        self.display()

    def on_cancel(self):
        self.status.value = ""
        self.parentApp.switchForm("MAIN")

    def exit_func(self, _input):
        exit(0)
