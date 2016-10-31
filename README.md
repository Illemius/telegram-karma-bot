# telegram-karma-bot
Calculate karma in telegram.

You can add this bot to any dialogs.

Copyright © 2016 Illemius Corp

License: http://opensource.org/licenses/MIT

Author: Alex Root Junior


# Setup
- `pip install requirements.txt`
- `chmod +x bot.sh`

### MongoDB

#### Debian/Ubuntu
```
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/debian wheezy/mongodb-org/3.0 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```
Manual: https://docs.mongodb.com/v3.0/tutorial/install-mongodb-on-debian/

#### ArchLinux
Install from official repository: `sudo pacman -Suy mongodb`

Manual: https://wiki.archlinux.org/index.php/MongoDB

# Start
Run: `./bot.sh start`

Run background: `./bot.sh bg`

Stop background: `./bot.sh stop`


# Telegram
Bot: [@TeleKarmaBot](https://telegra.me/TeleKarmaBot)

Testing dialog (RU): https://telegram.me/telekarmabot_debug

Logging: https://telegram.me/telekarmabot_logs

Author: [@JRootJunior](https://telegram.me/JRootJunior)
