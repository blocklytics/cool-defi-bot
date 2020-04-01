"""
Script creating and running flask instance which can start/stop telegram bot
Miha Lotric, Dec 2019
"""
from flask import Flask, request
from cool_defi_bot import telegram_bot
from cool_defi_bot import config
from dotenv import load_dotenv
import requests
import os


load_dotenv()  # Load keys from .env file
SLACK_KEY = os.getenv("SLACK_KEY")  # Slack key to send developers the errors and exceptions
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Telegram bot token

app = Flask(__name__)
# Add private variables to app
app._bot_is_live = False 
app._bot = telegram_bot.get_bot()  # Telegram bot instance
app._token = BOT_TOKEN


def notify_slack(msg, chat='dev-telegram-bot'):
    """Notify Slack when bot is turned off or on."""
    params = {'token': SLACK_KEY,
              'channel': chat,
              'text': msg,
              'icon_emoji': ':blocky-cool:',
              'username': 'Cool Defi Bot',
              'pretty': 1}
    url = config.URLS['slack_api']
    requests.get(url, params=params)


@app.route('/start', methods=['POST'])
def start():
    """If no bot is already running start it."""
    method = request.args.get('method', 'Unknown')  # Local/Staging/Production
    run_type = 'Auto' if request.args.get('auto') == 'true' else 'Manual'
    if not app._bot_is_live:
        app._bot_is_live = True
        # Starts the listening
        app._bot.start_polling()
        notify_slack(f'{run_type} {method} bot started as {str(app._bot).lstrip("<telegram.ext.updater.Updater object at ").rstrip(">")}') 
        return 'Bot started'
    else:
        return 'Already live'


@app.route('/stop', methods=['POST'])
def stop():
    """If bot is running stop it."""
    method = request.args.get('method', 'Unknown')  # Local/Staging/Production
    run_type = 'Auto' if request.args.get('auto') == 'true' else 'Manual'
    if app._bot_is_live:
        app._bot.stop()
        app._bot_is_live = False
        notify_slack(f'{run_type} {method} bot stopped as {str(app._bot).lstrip("<telegram.ext.updater.Updater object at ").rstrip(">")}')
        return 'Bot stopped'
    else:
        return 'Already down'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
