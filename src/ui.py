from src import npyscreen
from src.MainForm import MainForm
from src.ContactsForm import ContactsForm
from src.SendFileForm import SendFileForm


class App(npyscreen.StandardApp):

    def onStart(self):
        self.MainForm = self.addForm("MAIN", MainForm)
        self.ContactsForm = self.addForm("CONTACTS", ContactsForm)
        self.SendFileForm = self.addForm("SEND_FILE", SendFileForm, lines=15)
