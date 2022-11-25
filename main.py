#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Based on echobot (https://github.com/python-telegram-bot/python-telegram-bot/blob/v13.x/examples/echobot.py).
A bot that lets users send WOL magic packet after their respective MAC address is added to the list.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
User /register to register your Telegram account with bot.
After that, admin adds MAC address to the config file.
Then /wol can be used to wake up PCs.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import re

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from wakeonlan import send_magic_packet

config_file = 'telegram_bot_users'
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


# Create and/or parse config file with Telegram IDs and MAC addresses
def user_table(request):
    telegram_dict = {}
    table_header = ['    Full name    ', 'Username', 'Telegram ID', 'MAC address']
    table = open(config_file, 'a+')
    table.seek(0, 0)
    content = table.read()

    if re.search(r'^\s*$', content):
        with open(config_file, 'w') as fp:
            for item in table_header:
                fp.write("%s | " % item)
            fp.write("\n" + "-"*55)
    
    with open(config_file, 'r') as fp:
        for line in fp.readlines():
            try:
                telegram_id = line.rstrip('\n').split(' | ')[2]
                mac_address = line.rstrip('\n').split(' | ')[3]
                telegram_dict[telegram_id] = mac_address
            except:
                continue
    table.close()
    if request == 'users':
        return list(telegram_dict.keys())
    else:
        return telegram_dict


# Add user to config file
def register(update: Update, context: CallbackContext) -> None:
    """Add a user to user list to be later associated with MAC address."""
    user = update.message.from_user
    print('You talk with user {} ({}) and his user ID: {} '.format(user['full_name'], user['username'], user['id']))
    if str(user['id']) not in user_table('users'):
        with open(config_file, 'a') as fp:
            fp.write("\n" + user['full_name'] + " | " + user['username']  + " | " + str(user['id']) + " | ")
        update.message.reply_text('Registration complete! Notify your admin to update database with your MAC address.')
    else:
        update.message.reply_text('Seems like you are already registered! Try using /wol command.')


# Send WOL magic packet
def send_wol(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    mac_address = user_table('list')
    if str(user['id']) not in user_table('users'):
        update.message.reply_text('Seems like you are not registered! Use /register first.')
        return
    if mac_address[str(user['id'])] == '':
        update.message.reply_text('Your MAC address is missing in database! Contact your admin.')
        return
    try:
        send_magic_packet(mac_address[str(user['id'])])    
    except:
        update.message.reply_text('Something is broken! :( Please notify your admin.')
    finally:
        update.message.reply_text('WOL magic packet sent! Amazing!')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("register", register))
    dispatcher.add_handler(CommandHandler("wol", send_wol))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
