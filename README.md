# Cool DeFi Bot

[@cool_defi_bot](https://t.me/cool_defi_bot) is an open-source telegram bot for providing users with DeFi information.

# Contributing

Please log bugs and feature requests to issues. Develop and add your own features by creating a pull request.

## Deploying a local version for development

Install dependencies in a new virtual environment:

```bash
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

Create an `.env` file:

```bash
SLACK_KEY = xxxxx
BOT_TOKEN = xxxxx
POOLS_KEY = xxxxx
ANALYTICS_TOKEN = xxxxx
```

Run the application:

```bash
$ python main.py
```

Start the bot (in a separate terminal window):

```bash
$ curl -X POST -d '' "http://127.0.0.1:8080/start?method=Local"
```