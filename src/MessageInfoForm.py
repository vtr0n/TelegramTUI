import curses
import os
from src.telegramApi import client
from src import npyscreen


class MessageInfoForm(npyscreen.ActionForm):

    def create(self):
        self.name = "Upload File (Press TAB)"
        new_handlers = {
            # exit
            "^Q": self.exit_func,
            155: self.exit_func,
            curses.ascii.ESC: self.exit_func
        }
        self.add_handlers(new_handlers)


    def on_ok(self):
        pass

    def on_cancel(self):
        self.status.value = ""
        self.parentApp.switchForm("MAIN")

    def exit_func(self, _input):
        exit(0)
