from telethon import TelegramClient, events
import socks
import configparser
from datetime import timedelta

class TelegramApi:
    client = None
    dialogs = []
    messages = []

    need_update_message = 0
    need_update_online = 0
    need_update_current_user = -1
    need_update_read_messages = 0

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        api_id = config.get('telegram_api', 'api_id')
        api_hash = config.get('telegram_api', 'api_hash')
        workers = config.get('telegram_api', 'workers')
        session_name = config.get('telegram_api', 'session_name')

        self.timezone = int(config.get('other', 'timezone'))
        self.message_dialog_len = int(config.get('app', 'message_dialog_len'))

        # proxy settings
        if config.get('proxy', 'type') == "HTTP":
            proxy_type = socks.HTTP
        elif config.get('proxy', 'type') == "SOCKS4":
            proxy_type = socks.SOCKS4
        elif config.get('proxy', 'type') == "SOCKS5":
            proxy_type = socks.SOCKS5
        else:
            proxy_type = None
        proxy_addr = config.get('proxy', 'addr')
        proxy_port = int(config.get('proxy', 'port')) if config.get('proxy', 'port').isdigit() else None
        proxy_username = config.get('proxy', 'username')
        proxy_password = config.get('proxy', 'password')

        proxy = (proxy_type, proxy_addr, proxy_port, proxy_username, proxy_password)

        # create connection
        self.client = TelegramClient(session_name, api_id, api_hash, update_workers=int(workers),
                                     spawn_read_thread=True, proxy=proxy)
        self.client.start()

        self.me = self.client.get_me()
        self.dialogs = self.client.get_dialogs(limit=self.message_dialog_len)
        self.messages = len(self.dialogs) * [None]
        self.online = len(self.dialogs) * [""]
        self.messages[0] = self.client.get_message_history(self.dialogs[0].entity, limit=self.message_dialog_len)

        # event for new messages
        @self.client.on(events.NewMessage)
        def my_event_handler(event):
            for i in range(len(self.dialogs)):
                # if event message from user
                if hasattr(self.dialogs[i].dialog.peer, 'user_id') and hasattr(event._chat_peer, 'user_id') and \
                        self.dialogs[i].dialog.peer.user_id == event._chat_peer.user_id:
                    self.event_message(i)
                # from chat
                elif hasattr(self.dialogs[i].dialog.peer, 'chat_id') and hasattr(event._chat_peer, 'chat_id') and \
                        self.dialogs[i].dialog.peer.chat_id == event._chat_peer.chat_id:
                    self.event_message(i)
                # from chat
                elif hasattr(self.dialogs[i].dialog.peer, 'channel_id') and hasattr(event._chat_peer, 'channel_id') and \
                        self.dialogs[i].dialog.peer.channel_id == event._chat_peer.channel_id:
                    self.event_message(i)
                # other
                else:
                    pass

        # event for read messages
        @self.client.on(events.Raw(chats=None, blacklist_chats=False))
        def my_event_handler(event):
            if hasattr(event, 'confirm_received') and hasattr(event, 'max_id'):
                for i in range(len(self.dialogs)):
                    # from user
                    if hasattr(self.dialogs[i].dialog.peer, 'user_id') and hasattr(event.peer, 'user_id') and \
                            self.dialogs[i].dialog.peer.user_id == event.peer.user_id:
                        self.dialogs[i].dialog.read_outbox_max_id = event.max_id
                        self.need_update_current_user = i
                    # from chat
                    elif hasattr(self.dialogs[i].dialog.peer, 'chat_id') and hasattr(event.peer, 'chat_id') and \
                            self.dialogs[i].dialog.peer.chat_id == event.peer.chat_id:
                        self.dialogs[i].dialog.read_outbox_max_id = event.max_id
                        self.need_update_current_user = i
                    # other
                    else:
                        pass
                self.need_update_read_messages = 1

        # event for online/offline
        @self.client.on(events.UserUpdate(chats=None, blacklist_chats=False))
        def my_event_handler(event):
            for i in range(len(self.dialogs)):
                if hasattr(self.dialogs[i].dialog.peer, 'user_id') and hasattr(event._chat_peer, 'user_id') and \
                        self.dialogs[i].dialog.peer.user_id == event._chat_peer.user_id:
                    # I think need little bit change this
                    if event.online:
                        self.online[i] = "Online"
                    elif event.last_seen is not None:
                        self.online[i] = "Last seen at " + str(event.last_seen + (timedelta(self.timezone) // 24))
                    else:
                        self.online[i] = ""
                    self.need_update_current_user = i

            self.need_update_online = 1

    def event_message(self, user_id):
        if self.messages[user_id] is None:
            self.get_messages(user_id)
            new_message = self.client.get_message_history(self.dialogs[user_id].entity,
                                                          min_id=self.messages[user_id][0].id - 1)
        else:
            new_message = self.client.get_message_history(self.dialogs[user_id].entity,
                                                          min_id=self.messages[user_id][0].id)

        for j in range(len(new_message) - 1, -1, -1):
            self.messages[user_id].insert(0, new_message[j])
            self.dialogs[user_id].unread_count += 1

        self.messages[user_id].sort(key=lambda x: x.id, reverse=True)
        self.remove_duplicates(self.messages[user_id])

        self.need_update_message = 1
        self.need_update_current_user = user_id

    def get_messages(self, user_id):
        if self.messages[user_id] is None:
            data = self.client.get_message_history(self.dialogs[user_id].entity, limit=self.message_dialog_len)
            # need check exceptions
            self.messages[user_id] = data
            self.messages[user_id].sort(key=lambda x: x.id, reverse=True)
            return data
        else:
            return self.messages[user_id]

    def download_media(self, media, path):
        return self.client.download_media(media, path)

    def message_send(self, message, user_id):
        data = self.client.send_message(self.dialogs[user_id].entity, message)

        # read message
        self.client.send_read_acknowledge(self.dialogs[user_id].entity, max_id=data.id)

        # save message
        new_message = self.client.get_message_history(self.dialogs[user_id].entity, min_id=(data.id - 1))

        for j in range(len(new_message) - 1, -1, -1):
            self.messages[user_id].insert(0, new_message[j])

        self.messages[user_id].sort(key=lambda x: x.id, reverse=True)
        self.remove_duplicates(self.messages[user_id])

    def file_send(self, file, user_id, func):
        data = self.client.send_file(self.dialogs[user_id].entity, file, progress_callback=func)

        # save message
        new_message = self.client.get_message_history(self.dialogs[user_id].entity, min_id=(data.id - 1))

        for j in range(len(new_message) - 1, -1, -1):
            self.messages[user_id].insert(0, new_message[j])

        self.messages[user_id].sort(key=lambda x: x.id, reverse=True)
        self.remove_duplicates(self.messages[user_id])

    def read_all_messages(self, user_id):
        if hasattr(self.messages[user_id][0], 'id'):
            self.client.send_read_acknowledge(self.dialogs[user_id].entity,
                                              max_id=self.messages[user_id][0].id)

    def remove_duplicates(self, messages):
        i = 0
        while i < len(messages) - 1:
            if messages[i].id == messages[i + 1].id:
                del messages[i]
                i = i - 1

            i = i + 1

        return messages


client = TelegramApi()