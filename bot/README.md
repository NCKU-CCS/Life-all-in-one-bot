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

    git clone https://github.com/FrankYang0529/Install-Postgis.git
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
    CREATE ROLE bot_user PASSWORD ...

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

# file map
bot
|-bot
|-dashboard: for the frontend dashboard api
|-fb: for the fb chatbot
|-static: for the frontend dashboard setup
|-templates: for teh frontend dashboard setup

# fb

## script.py

### Insert data with script after migration
    echo 'import fb.script' | python manage.py shell --settings=bot.settings.local

## views.py

```
	certification(input_str)
```
- 用來處理證件辦理相關事項，input_str為證件類別

```
	joke()
```
- 用來隨機產生笑話
- 必須import random

```
	location(message)
```
- 用來抓取使用者位址
- message為entry 中 'messaging'項目的第一個陣列元素之'message'項目

```
	def restaurant(user_location, current_time):
```
- 回傳資料庫中的餐廳地址
- user_location為location function抓取到的位址
- current_time則是entry中的time項目

```
	def nearby_place(user_location, keyword):
```
- 回傳附近的位址
- keyword則是商家種類

```
	geo_distance(lon1, lat1, lon2, lat2)
```
- 取得兩位置之間的距離

#  dashboard

## models

### FSM
- state=0: first man, state=1: seen before two of them are normal

### TextCloud
- text紀錄文字雲的文字
- flag紀錄此文字我們是否可以處理
- number紀錄數量
