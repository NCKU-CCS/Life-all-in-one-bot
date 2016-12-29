import json
import requests
import jieba
import logging

import random
import time
import math
import codecs
import urllib
import urllib.request
from pprint import pprint

from django.conf import settings
from django.http import HttpResponse
from django.views import View
from dashboard.models import TextCloud
from dashboard.models import FSM

import random
from fb.models import Joke, Restaurant
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.forms.models import model_to_dict
from django.contrib.gis.db.models.functions import Distance

from django.db.models.query import QuerySet


class FBWebhook(View):

    def post(self, request, *args, **kwargs):
        msg_entries = json.loads(request.body.decode('utf-8'))
        post_msg_url = 'https://graph.facebook.com/v2.6/me/messages?access_token={token}'.format(token=settings.FB_TOKEN)
        pprint (msg_entries)
        for entry in msg_entries['entry']:
            for message in entry['messaging']:
                if message.get('sender', '') == {'id': '409598692761944'}:
                    continue
                #should change the id when publish
                # continue
                sender_url = 'https://graph.facebook.com/v2.6/{sender}?fields=first_name,last_name,gender&access_token={token}'\
                            .format(sender=message['sender']['id']\
                            ,token=settings.FB_TOKEN)
                sender_info = requests.get(sender_url).json()
                current_time = entry['time']
                ##classify the user id
                try:
                    search_id = FSM.objects.get(fb_id=str(message['sender']['id']))
                except:
                    search_id = FSM.objects.create(fb_id=str(message['sender']['id'])
                                                   ,first_name=sender_info['first_name']
                                                   ,last_name=sender_info['last_name']
                                                   ,gender=True
                                                   ,state=1)
                    if sender_info['gender'] == 'male':
                        search_id.gender = True
                    else:
                        search_id.gender = False
                    search_id.save()
                if message.get('message', '') != '':
                    ##classify the messange
                    ##state=0: first man, state=1: seen before two of them are normal
                    if message['message'].get('attachments', '') != '':
                        res_msg = attachments_deal(message,search_id,current_time)
                        if (isinstance(res_msg,str) and res_msg != False):
                            req = requests.post(post_msg_url,
                                                headers={"Content-Type": "application/json"},
                                                data=res_msg)
                            return HttpResponse(status=200)
                        elif (isinstance(res_msg,QuerySet) and res_msg != False):
                            for foo in res_msg:
                                res_json = json.dumps({
                                            "recipient": message['sender'],
                                            "message": {
                                                "text": foo.name
                                            }})
                                requests.post(post_msg_url,
                                            headers={"Content-Type": "application/json"},
                                            data=res_json)
                                res_json = json.dumps({
                                            "recipient": message['sender'],
                                            "message": {
                                                "text": foo.address
                                            }})
                                requests.post(post_msg_url,
                                            headers={"Content-Type": "application/json"},
                                            data=res_json)
                            return HttpResponse(status=200)
                        else:
                            continue
                    #user request to search nearby location,
                    #this message is keyword
                    if(search_id.state == 4):
                        search_id.state = 1
                        search_id.save()
                        res_msg = json.dumps({
                                        "recipient": message['sender'],
                                        "message": {
                                            "text":nearby_place(search_id.lat
                                                                ,search_id.lng
                                                                ,message['message']['text'])
                                        }})
                        pprint (res_msg)
                        req = requests.post(post_msg_url,
                                            headers={"Content-Type": "application/json"},
                                            data=res_msg)
                        return HttpResponse(status=200)
                    else:
                        #handle the text using jieba
                        keyword = msg_classify(message['message']['text'])
                        if(keyword != "trash"):
                            res_msg = json.dumps({
                                    "recipient": message['sender'],
                                    "message": {
                                            "text": msg_reply(keyword,search_id)
                                        }
                                    })
                            req = requests.post(post_msg_url,
                                                headers={"Content-Type": "application/json"},
                                                data=res_msg)
                            return HttpResponse(status=200)
                        else:
                            res_msg = json.dumps({
                                        "recipient": message['sender'],
                                        "message": {
                                        	"attachment":{
        										"type":"template",
        										"payload":{
        											"template_type":"button",
        											"text":"嗨,"+ sender_info['first_name'] + "!\n" +
        													"我是小歐(All in one)，你可以問我關於台南的相關訊息~ \
        													也歡迎你留下你的建議，讓我能提供的服務更豐富喔",
        											"buttons":[
        											  {
        											    "type":"postback",
        											    "title": "食物推薦",
        											    "payload": "food"
        											  },
        											  {
        											    "type":"postback",
        											    "title":"證件遺失了，救救我",
        											    "payload":"certification"
        											  },
                                                      {
                                                        "type":"postback",
                                                        "title":"看看我還能做什麼",
                                                        "payload":"more"
                                                      }
        											]
        										}
        									}
                                        }})
                            req = requests.post(post_msg_url,
                                                headers={"Content-Type": "application/json"},
                                                data=res_msg)
                            return HttpResponse(status=200)
                elif message.get('postback', '') != '':
                    res_msg = payload_classify(message,search_id)
                    req = requests.post(post_msg_url,
                                        headers={"Content-Type": "application/json"},
                                        data=res_msg)
                    return HttpResponse(status=200)
        return HttpResponse(status=200)
    def get(self, request, *args, **kwargs):
        verification_code = settings.VERIFICATION_CODE
        verify_token = request.GET.get('hub.verify_token', '')
        if verification_code != verify_token:
            print(verify_toke)
            return HttpResponse(status=400)

        return HttpResponse(request.GET.get('hub.challenge', ''), status=200)
###
def attachments_deal(message,search_id,current_time):
    if (message['message']['attachments'][0]['type'] == 'fallback'):
        # ignore the fallback attachments
        return False
    elif (search_id.state != 2 and search_id.state != 3):
        search_id.state = 1
        search_id.save()
        res_json = json.dumps({
                    "recipient": message['sender'],
                    "message": {
                        "text":"您似乎傳了一個附件給我，但我不明白為何您要傳給我\n"+\
                                "如果想要知道附近的美食資訊，請告訴我「美食」後再傳送位置"+\
                                "如果想要知道附近的商家資訊，請告訴我「商家」後再傳送位置"
                    }})
        return res_json
    else:
        if (search_id.state==2):
            location_detail = location(message['message'])
            if (location_detail == "failed"):
                search_id.state = 1
                search_id.save()
                res_json = json.dumps({
                            "recipient": message['sender'],
                            "message": {
                                "text":"抱歉，我不能解析這個位置"
                            }})
                return res_json
            else :
                search_id.lng = location_detail['long']
                search_id.lat = location_detail['lat']
                search_id.location = Point(float(search_id.lng), float(search_id.lat))
                search_id.state = 1
                search_id.save()
                return restaurant(location_detail,current_time)
        elif (search_id.state==3):
            location_detail = location(message['message'])
            if (location_detail == "failed"):
                search_id.state = 1
                search_id.save()
                res_json = json.dumps({
                            "recipient": message['sender'],
                            "message": {
                                "text":"抱歉，我不能解析這個位置"
                            }})
                return res_json
            else :
                search_id.lng = location_detail['long']
                search_id.lat = location_detail['lat']
                search_id.location = Point(float(search_id.lng), float(search_id.lat))
                search_id.state = 4
                search_id.save()
                res_json = json.dumps({
                            "recipient": message['sender'],
                            "message": {
                                "text":"請輸入你想查找的商家關鍵字"
                            }})
                return res_json
            pass
def payload_classify(message,search_id):
    if (message['postback']['payload'] == 'food'):
        res_json = json.dumps({
                        "recipient": message['sender'],
                        "message": {
                            "text": "那麼 請給我您的位置以便查詢附近商家"
                        }})
        search_id.state = 2
        search_id.save()
        return res_json
    elif (message['postback']['payload'] == 'certification'):
        search_id.state = 1
        search_id.save()
        res_json = json.dumps({
                        "recipient": message['sender'],
                        "message": {
                            "attachment": {
                                "type": "template",
                                "payload": {
                                    "template_type": "generic",
                                    "elements": [
                                        {
                                            "title": "身分證",
                                            # "subtitle": "Element #1 of an hscroll",
                                            # "image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                                            "buttons": [{
                                                "type": "postback",
                                                "title": "按我查詢",
                                                "payload": "ID",
                                            }],
                                        },
                                        {
                                            "title": "健保卡",
                                            # "subtitle": "Element #2 of an hscroll",
                                            # "image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
                                            "buttons": [{
                                                "type": "postback",
                                                "title": "按我查詢",
                                                "payload": "health",
                                            }],
                                        },
                                        {
                                            "title": "駕照",
                                            # "subtitle": "Element #2 of an hscroll",
                                            # "image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
                                            "buttons": [{
                                                "type": "postback",
                                                "title": "按我查詢",
                                                "payload": "drive",
                                            }],
                                        },
                                        {
                                            "title": "戶籍謄本",
                                            # "subtitle": "Element #2 of an hscroll",
                                            # "image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
                                            "buttons": [{
                                                "type": "postback",
                                                "title": "按我查詢",
                                                "payload": "household",
                                            }],
                                        }
                                    ]
                                }
                            }
                        }})
        return res_json
    elif (message['postback']['payload'] == 'ID'):
        search_id.state = 1
        search_id.save()
        res_json = json.dumps({
                        "recipient": message['sender'],
                        "message": {
                            "text": "電話申請掛失請直撥1996內政服務專線提出申請，"+
                                    "或是親自前往戶政事務所。"+
                                    "補領身分證須攜帶戶口名簿正本或其他有效證件，"+
                                    "以及正面半身彩色相片一張，還有當事人印章或簽名。"
                        }})
        build_text_cloud('身分證')
        return res_json
    elif (message['postback']['payload'] == 'health'):
        search_id.state = 1
        search_id.save()
        res_json = json.dumps({
                        "recipient": message['sender'],
                        "message": {
                            "text": "申請換補領健保IC卡時，請填寫「請領健保IC卡申請表」"+
                                    "，背面應黏貼身分證或其他身分證明文件正反面影本，"+
                                    "健保卡上如要印有照片，請貼上合規格照片。"+
                                    "接著請攜帶身分證明文件正本向各地郵局櫃檯、健保局各分局辦理，"+
                                    "工本費200元。"
                        }})
        build_text_cloud('健保卡')
        return res_json
    elif (message['postback']['payload'] == 'drive'):
        search_id.state = 1
        search_id.save()
        res_json = json.dumps({
                        "recipient": message['sender'],
                        "message": {
                            "text": "攜帶身分證或其他身分證明文件，"+
                                    "以及6個月內正面半身1吋照片兩張，"+
                                    "至監理所辦理，辦理規費200元。"
                        }})
        build_text_cloud('駕照')
        return res_json
    elif (message['postback']['payload'] == 'household'):
        search_id.state = 1
        search_id.save()
        res_json = json.dumps({
                        "recipient": message['sender'],
                        "message": {
                            "text": "攜帶身分證正本和印章，至任一戶政事務所辦理，"+
                                    "可以申請全戶或個人部份戶籍謄本，每張15元。"
                        }})
        build_text_cloud('戶籍謄本')
        return res_json
    elif (message['postback']['payload'] == 'more'):
        search_id.state = 1
        search_id.save()
        res_json = json.dumps({
                        "recipient": message['sender'],
                        "message": {
                            "attachment":{
                                "type":"template",
                                "payload":{
                                    "template_type":"button",
                                    "text":"我還能做這些事情唷！",
                                    "buttons":[
                                        {
                                            "type":"postback",
                                            "title":"說點笑話給你聽",
                                            "payload":"joke"
                                        },
                                        {
                                            "type":"postback",
                                            "title":"查看附近的商家或地標",
                                            "payload":"near_location"
                                        },
                                        {
                                            "type":"postback",
                                            "title":"設定個人化主動推播",
                                            "payload":"auto_info"
                                        }
                                    ]
                                }
                            }
                        }})
        return res_json
    elif (message['postback']['payload'] == 'joke'):
        search_id.state = 1
        search_id.save()
        res_json = json.dumps({
                "recipient": message['sender'],
                "message": {
                    "text": joke()
                }})
        build_text_cloud('笑話')
        return res_json
    elif (message['postback']['payload'] == 'near_location'):
        res_json = json.dumps({
                        "recipient": message['sender'],
                        "message": {
                            "text": "那麼 請給我您的位置以便查詢附近商家"
                        }})
        search_id.state = 3
        search_id.save()
        build_text_cloud('商家')
        return res_json

def msg_reply(keyword,search_id):
    # keyword = msg_classify(message['message']['text'],search_id)
    if (keyword == "weather"):
        #TODO
        return "none"
    elif (keyword == "food"):
        search_id.state = 2
        search_id.save()
        return "那麼 請給我您的位置以便查詢附近商家"
    elif keyword == "joke":
        search_id.state = 1
        search_id.save()
        return joke()
    elif keyword == "ID":
        search_id.state = 1
        search_id.save()
        return "電話申請掛失請直撥1996內政服務專線提出申請，或是親自前往戶政事務所" +\
                "。補領身分證須攜帶戶口名簿正本或其他有效證件，" +\
                "以及正面半身彩色相片一張，還有當事人印章或簽名。"
    elif keyword == "health":
        search_id.state = 1
        search_id.save()
        return "申請換補領健保IC卡時，請填寫「請領健保IC卡申請表」" +\
                "，背面應黏貼身分證或其他身分證明文件正反面影本，" +\
                "健保卡上如要印有照片+，請貼上合規格照片。" +\
                "接著請攜帶身分證明文件正本向各地郵局櫃檯、健保局各分局辦理，" +\
                "工本費200元。"
    elif keyword == "drive":
        search_id.state = 1
        search_id.save()
        return "攜帶身分證或其他身分證明文件，以及6個月內正面半身1吋照片兩張，" +\
                "至監理所辦理，辦理規費200元。"
    elif keyword == 'household':
        search_id.state = 1
        search_id.save()
        return "攜帶身分證正本和印章，至任一戶政事務所辦理，" +\
                "可以申請全戶或個人部份戶籍謄本，每張15元。"
    elif keyword == "near_location":
        search_id.state = 3
        search_id.save()
        return "那麼 請給我您的位置以便查詢附近商家"

def msg_classify(msg):
    jieba.set_dictionary('dict.txt.big')
    cut_msg = jieba.cut(msg)
    cut_msg_list = list()
    for foo in cut_msg:
        cut_msg_list.append(foo)

    accept_word = {'天氣':"weather",
                '美食':"food" ,
                '笑話':"joke" ,
                '身分證':"ID",
                '健保卡':"health",
                '駕照':"drive",
                '戶籍謄本':"household",
                '商家':"near_location"
                }
    useless_dictionary = ['是','不是','你','?','.','？','。','我','的','想要']
    category = 'trash'

    for key in cut_msg_list:
        if key in accept_word.keys():
            category = accept_word.get(key,"trash")#default is trash
            for bar in cut_msg_list:
                if bar in useless_dictionary:
                    continue
                build_text_cloud(key)
            break
        else:
            #if no break=>no match accept_word
            # category = "trash"
            build_text_cloud(msg)

    return category

def build_text_cloud(msg):
    try:
        search_data = TextCloud.objects.get(text=msg)
    except:
        search_data = TextCloud.objects.create(text=msg, number=0,flag=False)
    search_data.number += 1
    search_data.save()

def joke():
    joke_count = Joke.objects.all().count()
    index = random.randint(0, joke_count-1)

    joke = object()
    while(1):
        try:
            joke = Joke.objects.get(pk=index)
            if( len(joke.context) > 300 ):
                continue
            break
        except self.model.DoesNotExist:
            continue

    response_str = joke.title + "\n" + joke.context

    return response_str

def location(message):
    #TODO
    #should edit to verify with the attachments type
    if message['attachments'][0]['payload'].get('coordinates', '') == '':
        return 'failed'
    else:
        return message['attachments'][0]['payload']['coordinates']


def restaurant(user_location, current_time):
    clock = time.gmtime(current_time/1000).tm_hour + 8#should be edited if the time zone is not +8
    if clock > 24:
        clock - 24
    meal_category = str()
    if clock <= 10:
        meal_category = "早餐"
    elif clock <= 15:
        meal_category = "午餐"
    else:
        meal_category = "晚餐"

    lng = user_location['long']
    lat = user_location['lat']
    point = Point(lng, lat, srid=4326)
    restaurant_set = Restaurant.objects\
    .filter(category__contains=[meal_category])\
    .exclude(lng=0)\
    .annotate(distance=Distance('location', point))\
    .filter(location__distance_lte=(point, D(km=3)))\
    .order_by('distance')[:5]\

    return restaurant_set

def nearby_place(user_lat, user_lng, keyword):
    params = {
            'location': (str(user_lat) + ',' + str(user_lng)),
            'rankby' : 'distance',
            'keyword' : keyword,
            'language' : 'zh-TW',
            'key' : 'AIzaSyAljxcakDVu_Cbz21iMpUx-4XPYqLGcU-U',
    }
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?' + urllib.parse.urlencode(params)
    response = urllib.request.urlopen(url)
    reader = codecs.getreader("utf-8")
    result = json.load(reader(response))

    pprint (result)
    response_str = str()
    try:
        result_list = result['results']
        if len(result_list) >= 3 :
            for i in range(0, 3) :
                lng = result_list[i]['geometry']['location']['lng']
                lat = result_list[i]['geometry']['location']['lat']
                response_str = response_str + result_list[i]['name'] + ' ( 距離'\
                               + str(geo_distance(user_lng, user_lat, lng, lat))\
                               + 'm )' + '\n' + result_list[i]['vicinity'] + '\n\n'
        else :
            for element in result_list :
                lng = result_list[i]['geometry']['location']['lng']
                lat = result_list[i]['geometry']['location']['lat']
                # print(distance(user_lng, user_lat, lng, lat))
                response_str = response_str + result_list[i]['name'] + ' ( 距離'\
                               + str(geo_distance(user_lng, user_lat, lng, lat))\
                               + 'm )' + '\n' + result_list[i]['vicinity'] + '\n\n'
        return  response_str
    except Exception as e:
        print (e)
        return 'not found'


def geo_distance(lon1, lat1, lon2, lat2):
    radius = 6371 # km
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = float("{0:.3f}".format(radius * c))
    return int(d*1000)