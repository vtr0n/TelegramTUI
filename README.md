# TelegramTUI
Telegram client on your console

![telegram](https://user-images.githubusercontent.com/18473198/37569384-a4d32e70-2af2-11e8-948c-5a177b384657.png)

### Dependencies
* [Telethon](https://github.com/LonamiWebs/Telethon)
* [NpyScreen](https://github.com/bad-day/npyscreen)
* [python-aalib](http://jwilk.net/software/python-aalib)

### Installation
#### Debian based
```shell 
sudo apt-get install git python python3-pip aalib1
sudo pip3 install pillow telethon python-aalib 
git clone https://github.com/bad-day/TelegramTUI  
cd TelegramTUI  
```
#### Arch linux
```shell 
sudo pacman -S git python3 python-pip aalib
sudo pip3 install pillow telethon python-aalib 
git clone https://github.com/bad-day/TelegramTUI  
cd TelegramTUI  
```

### Usage
* [Create application](https://core.telegram.org/api/obtaining_api_id)  
* Put **api_id** and **api_hash** into **config.ini**  
* Run `./telegramTUI`

### Controls
* Navigation: `Tab`, `Shift+Tab`, `mouse`  
* Send message: `Ctrl+S`, `Alt+Enter`  
* Exit: `Ctrl+Q`, `ESC`  
* Paste: `Shift+INS`
