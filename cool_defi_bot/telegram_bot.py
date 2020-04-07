"""
Script handling telegram commands.
Miha Lotric, Dec 2019
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ChatAction
from telegram.ext import CommandHandler, Updater
from telegram.ext.dispatcher import run_async
from dotenv import load_dotenv
import requests
import os
import traceback
import logging

from cool_defi_bot.api.custom_exceptions import APIError, DataError, FormatError
from cool_defi_bot.api import api_handlers
from cool_defi_bot import config
try:
    from private import private_features
except ModuleNotFoundError:
    private_features = None


load_dotenv()  # Load keys from .env file
TOKEN = os.getenv('BOT_TOKEN')  # Telegram bot token
SLACK_KEY = os.getenv("SLACK_KEY")  # Slack key to send developers the errors and exceptions
POOLS_KEY = os.getenv("POOLS_KEY")  # Blocklytics pools API key
ANALYTICS_TOKEN = os.getenv("ANALYTICS_TOKEN")  # Analytics key to track usage of the bot

# TODO config file + automate the formatting
welcome_text = """
<b>👋 Welcome!</b>\n
Get started:
<code>/pools dai</code>
<code>/deepest</code>
<code>/dexag dai</code>
<code>/paraswap dai</code>
<code>/0x</code>
<code>/feedback</code>
<code>/help</code>
"""
help_text = """
👉 <b>With this bot you can...</b>\n
See returns for Uniswap pools
<code>/pools DAI</code>\n
See the five deepest liquidity pools
<code>/deepest</code>\n
See the best <a href="https://dex.ag">dex.ag</a> prices
<code>/dexag DAI</code>
<code>/dexag 500 DAI</code>
<code>/dexag 500 DAI MKR</code>
<code>/dexag ETH 1 MKR</code>\n
See the best <a href="https://paraswap.io/">paraswap</a> prices
<code>/paraswap DAI</code>
<code>/paraswap 500 DAI</code>
<code>/paraswap 500 DAI MKR</code>\n
See the best <a href="https://0x.org">0x</a> prices
<code>/0x DAI</code>
<code>/0x 500 DAI</code>
<code>/0x 500 DAI MKR</code>
<code>/0x ETH 1 MKR</code>\n
Submit feedback 
<code>/feedback {your feedback}</code>
"""


@run_async
def start(update, context):
    """Send the user welcome message and possible commands."""
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text=welcome_text, 
                             parse_mode=ParseMode.HTML)
    # We use `effective_message` instead of `message` to handle situations when the
    # original message is deleted or edited - same for `effective_chat`
    post_analytics(update.effective_message)


@run_async
def help_(update, context):
    """Send user examples of commands."""
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=help_text, 
                             parse_mode=ParseMode.HTML, 
                             disable_web_page_preview=True)
    post_analytics(update.effective_message)


@run_async
def pools(update, context):
    """Send user annualized returns for requested token."""
    # Jumping dots animation indicating that bot is writing a response
    context.bot.sendChatAction(chat_id=update.effective_message.chat_id, 
                               action=ChatAction.TYPING)
    error_msg = pass_exception = None
    # Calling module for formatted data and token address
    try:
        response, address = api_handlers.get_pool(list(context.args))
        keyboard = [[InlineKeyboardButton(text="pools.fyi",
                                          url=f"{config.URLS['pools_token_site']}/{address}")]]
        button = InlineKeyboardMarkup(keyboard)
    except Exception as e:
        error_msg = traceback.format_exc()  # Get full error message
        pass_exception, response = check_exceptions(e)  # Respond appropriately depending on exception
        button = None
    finally:
        # Sending the message
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text=response, 
                                 reply_markup=button, 
                                 parse_mode=ParseMode.HTML, 
                                 disable_web_page_preview=True)
        post_analytics(update['message'])
        if pass_exception:
            send_exception(update['message'].text, error_msg)  # Send exception to Slack


@run_async
def deepest(update, context):
    """Send user 5 tokens with biggest liquidities."""
    # Jumping dots animation indicating that bot is writing a response
    context.bot.sendChatAction(chat_id=update.effective_message.chat_id, 
                               action=ChatAction.TYPING)
    error_msg = pass_exception = None
    # Calling module for formatted data and token address
    try:
        response = api_handlers.get_deepest()
        # Button with URL redirect below the message
        keyboard = [[InlineKeyboardButton(text="pools.fyi",
                                          url=config.URLS['pools_site'])]]
        button = InlineKeyboardMarkup(keyboard)
    except Exception as e:
        error_msg = traceback.format_exc()
        pass_exception, response = check_exceptions(e)
        button = None
    finally:
        # Sending the message
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text=response, 
                                 parse_mode=ParseMode.HTML,
                                 reply_markup=button)
        post_analytics(update['message'])
        if pass_exception:
            send_exception(update['message'].text, error_msg)


@run_async
def aggregator_offer(update, context, aggregator):
    # Jumping dots animation indicating that bot is writing a response
    context.bot.sendChatAction(chat_id=update.effective_message.chat_id, 
                               action=ChatAction.TYPING)
    error_msg = pass_exception = None
    # Calling module for formatted data and token address
    try:
        response = api_handlers.get_aggregator_offer(list(context.args), aggregator)
        # Button with URL redirect below the message
        url = config.URLS['aggregators'][aggregator]['site']
        keyboard = [[InlineKeyboardButton(text=aggregator, 
                                          url=url)]]
        button = InlineKeyboardMarkup(keyboard)
    except Exception as e:
        error_msg = traceback.format_exc()
        pass_exception, response = check_exceptions(e)
        button = None
    finally:
        # Sending the message
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text=response, 
                                 parse_mode=ParseMode.HTML,
                                 reply_markup=button)
        post_analytics(update['message'])
        if pass_exception:
            send_exception(update['message'].text, error_msg)


@run_async
def feedback(update, context):
    """Send user feedback to slack telegram-bot chat-room."""
    response1 = "<b>Sent</b>\nThank you for your feedback!"
    response2 = "<b>How to submit feedback</b>\n<code>/feedback your message</code>"
    empty = update.effective_message['text'].rstrip(' ') == '/feedback'
    # Chat data
    username = update.effective_message.from_user['username']
    user = f"{update.effective_message.from_user['first_name']} {update.effective_message.from_user['last_name']}"
    chat_id = update.effective_message['chat']['id']
    chat_type = update.effective_message['chat']['type']  # Group or private
    feedback_msg = update.effective_message['text'].lstrip('/feedback ')
    # Sending a response
    response = response1 if not empty else response2
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text=response, 
                             parse_mode=ParseMode.HTML)
    post_analytics(update.effective_message)
    final_msg = f"*Feedback from user {user}(@{username})*\n" \
                f"From chat: {chat_id} - " \
                f"({chat_type} {'' if chat_type == 'private' else update.effective_message['chat']['title']})\n" \
                f"> {feedback_msg}"
    # Sending a slack message to the telegram-bot chat-room
    params = {'token': SLACK_KEY,
              'channel': 'telegram-bot',
              'text': final_msg,
              'icon_emoji': ':blocky-thinking:',
              'username': 'telegram_bot',
              'pretty': 1}
    url = config.URLS['slack_api']
    # Send message only if it contains something
    if not empty:
        requests.get(url, params=params)


# todo make slack helper function
def send_exception(command, error_msg):
    """Send exception to slack telegram-bot chat-room."""
    print(error_msg)
    final_msg = f"*Beep-Bop, error found!*\n" \
                f"`{command}`\n" \
                f"```{error_msg}```"
    # Sending an error response to the slack telegram-bot chat-room
    params = {'token': SLACK_KEY,
              'channel': 'dev-telegram-bot',
              'text': final_msg,
              'icon_emoji': ':blocky-sweat:',
              'username': 'Cool Defi Bot',
              'pretty': 1
              }
    url = config.URLS['slack_api']
    requests.get(url, params=params)


def check_exceptions(exception):
    """Returns exception response and if it should be passed to devs, depending on type of exception."""
    if type(exception) in (DataError, FormatError):
        return False, str(exception)
    elif type(exception) == APIError:
        return True, str(exception)
    else:
        return True, "<b>There has been an error, sorry for inconvenience.</b>\nError was sent to devs."


def post_analytics(msg):
    """Pass message info to google analytics."""
    sender = msg.from_user
    chat = msg.chat
    # Apply to your own bot tokens
    bot_type = {'2qFI': 'local',
                'fVM0': 'staging',
                'w8eU': 'production'
                }
    command = msg.text.split()[0]
    # Where events are happening
    params_page = {'v': 1,
                   'tid': ANALYTICS_TOKEN,  # Analytics account
                   'cid': str(hash(str(sender.id))),  # *senderId
                   't': 'pageview',  # Hit type
                   'dt': str(hash(str(chat.id))),  # chatId
                   }
    # What events are happening
    params_event = {'v': 1,
                    'tid': ANALYTICS_TOKEN,
                    'cid': str(hash(str(sender.id))),  # *senderId
                    't': 'event',  # Hit type
                    'ec': 'bot command',  # type of command
                    'ea': command.lstrip('/'),  # command (eg. dexag)
                    'ds': bot_type.get(TOKEN[-4:], 'Unknown')  # local/staging/production bot
                    }
    # *senderId is a unique number indicating a user or a group. Bot uses it to send messages to the user/group and the
    # easiest way to find your id is with @jsondumpbot. We collect ids to track how many unique users there are.
    url = config.URLS['analytics']
    requests.post(url, params_page)
    requests.post(url, params_event)


def get_bot():
    """Create and return telegram bot instance."""
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # Create a bot instance
    updater = Updater(token=TOKEN, use_context=True, workers=50)
    dispatcher = updater.dispatcher

    # Setting funs to pass argument to the handler's callback function
    def dexag(update, context): aggregator_offer(update, context, 'dexag')
    def paraswap(update, context): aggregator_offer(update, context, 'paraswap')
    def oneinch(update, context): aggregator_offer(update, context, 'oneinch')
    def zerox(update, context): aggregator_offer(update, context, 'zerox')

    private_pairs = [] if not private_features else private_features.get_feature_pairs()
    public_pairs = [
        ('help', help_),
        ('start', start),
        ('pools', pools),
        ('deepest', deepest),
        ('dexag', dexag),
        # ('1inch', oneinch),  # Devs decided to exclude 1inch service for now
        ('paraswap', paraswap),
        ('0x', zerox),
        ('feedback', feedback)
    ]
    # Set handlers
    handlers = [CommandHandler(*pair) for pair in (public_pairs + private_pairs)]
    # Add handlers
    for handler in handlers:
        dispatcher.add_handler(handler)

    return updater
