# bot

* Python 3.5
* Django 1.10.2

## Setup

### Create virtualenv

macOS

    pyvenv venv

### Change virtualenv

	source venv/bin/activate

### Install packages

	cd ~/Life-all-in-one-bot
	pip install -r reuqirements.txt

### Secret key File

Create ~/Life-all-in-one-bot/bot/.secrets.json

    {
        "verification_code": "xxx",
        "FB_TOKEN": "xxx"
    }


## Start Server

### Local Server

	python manage.py runserver --settings=bot.settings.local

### Production Server

    sudo uwsgi --ini bot.ini


## Stop Server

### Production Server

    sudo killall -s INT uwsgi
