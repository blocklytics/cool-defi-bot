# Cool DeFi Bot

<img src="https://github.com/blocklytics/brand-resources/raw/master/emoji/cool.png" width=180 />

[@cool_defi_bot](https://t.me/cool_defi_bot) is an open-source telegram bot written in Python.

#### Features include:
- Fetch and format API data
- Report errors and feedback to Slack
- Record usage to Google Analytics
- Manage deployment with Flask application


# Contributing

Please log bugs and feature requests to issues. Develop and add your own features by creating a pull request.

## Deploying a local version for development

#### Install dependencies in a new virtual environment:

```bash
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

#### Create an `.env` file:

```bash
SLACK_KEY = xxxxx
BOT_TOKEN = xxxxx
POOLS_KEY = xxxxx
ANALYTICS_TOKEN = xxxxx
```
Only `BOT_TOKEN` is needed to run the bot, other just enable additional features, like error and feedback response via Slack and tracking command popularity via Analytics. `POOLS_KEY` is needed to run `/pools` and `/deepest` command - fill [the form](https://blocklytics.typeform.com/to/H4MBia) to get it.
 
#### Run the application locally:
```bash
$ python run_telegram.py
```
#### Run the application with Flask:
 - Run Flask instance:
	```bash
	$ python run_flask.py
	```
 - Start the bot with:
	```bash
	$ curl -X POST -d '' "http://127.0.0.1:8080/start?method=Local"
	```
 -  Stop the bot with:
	```bash
	$ curl -X POST -d '' "http://127.0.0.1:8080/stop?method=Local"
	```