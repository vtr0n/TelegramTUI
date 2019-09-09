# TelegramTUI
Telegram client on your console

![telegram](https://user-images.githubusercontent.com/18473198/37569384-a4d32e70-2af2-11e8-948c-5a177b384657.png)

### Dependencies
* [Telethon](https://github.com/LonamiWebs/Telethon)
* [NpyScreen](https://github.com/bad-day/npyscreen)
* [python-aalib](http://jwilk.net/software/python-aalib)

### Installation
* Create [telegram application](https://core.telegram.org/api/obtaining_api_id).
* Install pipenv ```pip install pipenv```.
* Clone repo ```git clone https://github.com/bad-day/TelegramTUI && cd TelegramTUI```.
* Install requirements ```pipenv install```.
* Copy config.ini.sample to config.ini ```cp config.ini.sample config.ini```.
* Put **api_id** and **api_hash** into **config.ini** ```vim config.ini```.
* Run TelegramTUI ```pipenv run ./telegramTUI```.

### Proxy
You can set proxy in config.ini

### Controls
* Navigation: `Tab`, `Shift+Tab`, `Mouse`
* Send message: `Ctrl+S`, `Alt+Enter`  
* Delete message: `Ctrl+R`
* Send file: `Ctrl+O`
* Exit: `Ctrl+Q`, `ESC`  
* Copy: `Shift+Mouse`
* Paste: `Shift+Ins`, `Shift+Middle mouse button`
