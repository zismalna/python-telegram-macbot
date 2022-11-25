# Telegram bot to wake up user PCs

## Dependencies:
```
pip install python-telegram-bot
pip install wakeonlan
```

## Usage:

Use */register* to register your Telegram account with bot.
After that, admin adds MAC address to the config file.
Then */wol* can be used to wake up PCs.
Press Ctrl-C on the command line or send a signal to the process to stop the bot.

## Integration
The config file is created in the directory the programm is running by default. You can change it by editing *config_file* value.
Can be self-started and monitored by using systemd unit file.

## Testing
Tested on Ubuntu 22.04.1 LTS, Python 3.10.6

## TODO
Add buttons if needed, test further.
