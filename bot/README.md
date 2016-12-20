# bot

* Python 3.5
* Django 1.10.2

## Setup

### Create virtualenv

macOS

    pyvenv venv
    
ubuntu

    virtualenv -p python3 venv

### Change virtualenv

	source venv/bin/activate

### Install packages

	cd ~/Life-all-in-one-bot
	pip install -r reuqirements.txt

### Install Postgresql & Postgis

#### ubuntu

    git cloen https://github.com/FrankYang0529/Install-Postgis.git
    cd Install-Postgis
    sudo ./install_postgis.sh

#### macOS

    brew install postgresql
    brew install postgis
    brew install gdal
    brew install libgeoip

### Create user, database & Grant

#### Change to postgres

    sudo su postgres

#### Create user

    createuser -P -e bot_user
    Enter password for new role: bot
    Enter it again: bot
    CREATE ROLE dengue_user PASSWORD ...

#### Create db

    createdb bot_db

#### Grant

    $: psql
    postgres=# GRANT ALL PRIVILEGES ON DATABASE bot_db TO bot_user;
    postgres=# \c bot_db;
    bot_db=# CREATE EXTENSION postgis;
    CREATE EXTENSION

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

    sudo uwsgi --ini bot.ini --touch-reload=/home/ubuntu/Life-all-in-one-bot/bot/bot.ini

## Stop Server

### Production Server

    sudo killall -s INT uwsgi
    
## Database setup
### Insert data with script after migration
    echo 'fb.script' | python manage.py shell --settings=bot.settings.local
    
