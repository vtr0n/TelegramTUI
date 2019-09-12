import os, configparser, errno


def get_config():
    user_config_dir = os.path.expanduser("~")
    config = configparser.ConfigParser(allow_no_value=True)

    filename = user_config_dir + '/.config/telegramtui/telegramtui.ini'
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    # if default config is npt exist
    if not os.path.isfile(filename):
        _create_default_config(config, filename)

    config.read(filename)

    # check config is valid
    _check_config(config, filename)

    return config


def _create_default_config(configparser, filename):
    configparser.add_section('telegram_api')
    configparser.set('telegram_api', '; obtain api keys here: https://core.telegram.org/api/obtaining_api_id')
    configparser.set('telegram_api', '; only api_id and api_hash are needed for the application to work')
    configparser.set('telegram_api', 'api_id', '*api_id here*')
    configparser.set('telegram_api', 'api_hash', '*api_hash here*')
    configparser.set('telegram_api', '; number of thread to receive data from tg api')
    configparser.set('telegram_api', 'workers', '3')
    configparser.set('telegram_api', '; you can use few accounts, change session name')
    configparser.set('telegram_api', 'session_name', 'user')

    configparser.add_section('app')
    configparser.set('app', 'name', 'TelegramTUI v0.1.1')
    configparser.set('app', 'message_dialog_len', '50')

    configparser.add_section('proxy')
    configparser.set('proxy', 'type', '*[SOCKS4|SOCKS5|HTTP]*')
    configparser.set('proxy', 'addr', '*ip add here*')
    configparser.set('proxy', 'port', '*port here*')
    configparser.set('proxy', '; set username and password (only for SOCKS)')
    configparser.set('proxy', 'username', 'None')
    configparser.set('proxy', 'password', 'None')

    configparser.add_section('other')
    configparser.set('other', 'timezone', '+0')
    configparser.set('other', 'emoji', 'False')
    configparser.set('other', 'emoji', 'False')
    configparser.set('other', '; ASCII image art')
    configparser.set('other', 'aalib', 'False')
    configparser.set('other', 'config_version', '1')

    configparser.write(open(filename, 'w'))


def _check_config(configparser, filename):
    api_id = configparser.get('telegram_api', 'api_id')
    api_hash = configparser.get('telegram_api', 'api_hash')

    if api_id == '*api_id here*' or api_hash == 'api_hash':
        print('Please, edit the config file: ' + filename)
        exit(1)
