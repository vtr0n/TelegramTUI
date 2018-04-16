from src import npyscreen
from src.MainForm import MainForm
from src.ContactsForm import ContactsForm
from src.SendFileForm import SendFileForm
from src.MessageInfoForm import MessageInfoForm
from src.ForwardMessageForm import ForwardMessageForm
from src.RemoveMessageForm import RemoveMessageForm


class App(npyscreen.StandardApp):

    def onStart(self):
        self.MainForm = self.addForm("MAIN", MainForm)
        self.ContactsForm = self.addForm("CONTACTS", ContactsForm)
        self.SendFileForm = self.addForm("SEND_FILE", SendFileForm, lines=15)
        self.MessageInfoForm = self.addForm("MESSAGE_INFO", MessageInfoForm)
        self.ForwardMessageForm = self.addForm("FORWARD_MESSAGE", ForwardMessageForm)
        self.RemoveMessageForm = self.addForm("REMOVE_MESSAGE", RemoveMessageForm, lines=5, columns=20)
