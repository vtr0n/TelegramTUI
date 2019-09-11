from telegramtui.src import npyscreen
from telegramtui.src.MainForm import MainForm
from telegramtui.src.ContactsForm import ContactsForm
from telegramtui.src.SendFileForm import SendFileForm
from telegramtui.src.MessageInfoForm import MessageInfoForm
from telegramtui.src.ForwardMessageForm import ForwardMessageForm
from telegramtui.src.RemoveMessageForm import RemoveMessageForm


class App(npyscreen.StandardApp):

    def onStart(self):
        self.MainForm = self.addForm("MAIN", MainForm)
        self.ContactsForm = self.addForm("CONTACTS", ContactsForm)
        self.SendFileForm = self.addForm("SEND_FILE", SendFileForm, lines=15)
        self.MessageInfoForm = self.addForm("MESSAGE_INFO", MessageInfoForm)
        self.ForwardMessageForm = self.addForm("FORWARD_MESSAGE", ForwardMessageForm)
        self.RemoveMessageForm = self.addForm("REMOVE_MESSAGE", RemoveMessageForm, lines=5, columns=20)
