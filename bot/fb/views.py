import json
import requests
import jieba

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


class FBWebhook(View):

    def post(self, request, *args, **kwargs):
        msg_entries = json.loads(request.body.decode('utf-8'))
        print('='*20 + 'receive' + '='*20)
        pprint (msg_entries)
        print('='*40)
        post_msg_url = 'https://graph.facebook.com/v2.6/me/messages?access_token={token}'.format(token=settings.FB_TOKEN)
        for entry in msg_entries['entry']:
            for message in entry['messaging']:
                if message.get('message', '') == '':
                    continue
                if message.get('sender', '') == {'id': '409598692761944'}:
                #should change the id when publish
                    continue
                print('-'*40)
                print(message)
                print('-'*40)
                sender_url = 'https://graph.facebook.com/v2.6/{sender}?fields=first_name,last_name,gender&access_token={token}'\
                            .format(sender=message['sender']['id']\
                            ,token=settings.FB_TOKEN)
                sender_info = requests.get(sender_url).json()
                current_time = entry['time']
                ##classify the user id
                try:
                    search_id = FSM.objects.get(fb_id=str(id))
                except:
                    search_id = FSM.objects.create(fb_id=str(id),first_name=sender_info['first_name'],last_name=sender_info['last_name'],gender=True,state=0)
                    # greeting += "歡迎使用Life-all-in-one BOT \t" +\
                    #             sender_info['first_name'] +\
                    #             "\n這是我第一次為你服務，我很榮幸\n"
                    if sender_info['gender'] == 'male':
                        search_id.gender = True
                    else:
                        search_id.gender = False
                    search_id.save()

                ##classify the messange
                ##state=0: first man, state=1: seen before two of them are normal
                reply = ''
                if (('attachments' in message['message'])):
                    if (message['message']['attachments'][0]['type'] == 'fallback'):
                        # ignore the fallback attachments
                        # pass
                        print('ignore this messange')
                        # return HttpResponse(status=200)
                    elif (search_id.state != 2):
                        reply = "您似乎傳了一個位置給我，但我不明白為何您要傳給我\n\
                                如果想要知道附近的美食資訊，請告訴我「美食」再傳送位置"
                        search_id.state = 1
                        search_id.save()
                else:
                    if (search_id.state==2):
                        location_detail = location(message['message'])
                        if (location_detail == "failed"):
                            search_id.state = 1
                            search_id.save()
                            reply = "抱歉，我不能解析這個位置"
                        else :
                            search_id.lng = location_detail['long']
                            search_id.lat = location_detail['lat']
                            search_id.location = Point(float(search_id.lng), float(search_id.lat))
                            search_id.state = 1
                            search_id.save()
                            reply = restaurant(location_detail,current_time)
                    else :
                        classify = msg_classify(message['message']['text'])
                        if classify=="weather":
                            pass
                        elif classify=="food":
                            search_id.state=2
                            reply = "那麼 請給我您的位置以便查詢附近商家"
                            search_id.save()
                        elif classify=="joke":
                            joke()
                        # elif classify=="cerification":
                            # certification()
                            #TODO? ask frank senpai
                        elif classify=="trash":
                            reply = "不要講垃圾話好ㄇ"
                        else:#cerification
                            cerification(classify)
                res_msg = json.dumps({
                                        "recipient": message['sender'],
                                        "message": {
                                            "text": reply
                                        }})
                req = requests.post(post_msg_url,
                                    headers={"Content-Type": "application/json"},
                                    data=res_msg)
        return HttpResponse(status=200)

    def get(self, request, *args, **kwargs):
        verification_code = settings.VERIFICATION_CODE
        verify_token = request.GET.get('hub.verify_token', '')
        if verification_code != verify_token:
            print(verify_toke)
            return HttpResponse(status=400)

        return HttpResponse(request.GET.get('hub.challenge', ''), status=200)
###
def msg_classify(msg):
    jieba.set_dictionary('dict.txt.big')
    cut_msg = jieba.cut(msg)
    cut_msg_list = list()
    for foo in cut_msg:
        cut_msg_list.append(foo)
    accept_word = {'天氣':"weather",
                '美食':"food" ,
                '笑話':"joke" ,
                '身分證':"certification",
                '健保卡':"certification",
                '駕照':"certification",
                '戶籍謄本':"certification"}
    useless_dictionary = ['是','不是','你','?','.','？','。','我','的','想要']
    category = "trash"
    for key in cut_msg_list:
        if key in accept_word.keys():
            category = accept_word.get(key,"trash")#default is trash
            if(category == "cerfification"):
                category = key
            for bar in cut_msg_list:
                if bar in useless_dictionary:
                    continue
                try:
                    search_data = TextCloud.objects.get(text=key)
                except:
                    search_data = TextCloud.objects.create(text=key, number=0,flag=True)
                search_data.number += 1
                search_data.save()
            break
        else:
            category = "trash"
            try:
                search_data = TextCloud.objects.get(text=msg)
            except:
                search_data = TextCloud.objects.create(text=msg, number=0,flag=False)
            search_data.number += 1
            search_data.save()

    return category

def certification(input_str):
    response_str = str()
    if input_str == '身分證':
        response_str = '電話申請掛失請直撥1996內政服務專線提出申請，或是親自前往戶政事務所。補領身分證須攜帶戶口名簿正本或其他有效證件，以及正面半身彩色相片一張，還有當事人印章或簽名。'
    elif input_str == '健保卡':
        response_str = '申請換補領健保IC卡時，請填寫「請領健保IC卡申請表」，背面應黏貼身分證或其他身分證明文件正反面影本，健保卡上如要印有照片，請貼上合規格照片。接著請攜帶身分證明文件正本向各地郵局櫃檯、健保局各分局辦理，工本費200元。'
    elif input_str == '駕照':
        response_str = '攜帶身分證或其他身分證明文件，以及6個月內正面半身1吋照片兩張，至監理所辦理，辦理規費200元。'
    elif input_str == '戶籍謄本':
        response_str = '攜帶身分證正本和印章，至任一戶政事務所辦理，可以申請全戶或個人部份戶籍謄本，每張15元。'
    else:
        response_str = 'Hello'

    return response_str


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
    if message.get('attachments', '') == '':
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

        response_str = str()
        for x in restaurant_set :
                s = x.name + "\n" + x.address + "\n\n"
                response_str = response_str + s

        return response_str

def nearby_place(user_location, keyword):
        params = {
                'location': (str(user_location['lat']) + ',' + str(user_location['long'])),
                'rankby' : 'distance',
                'keyword' : keyword,
                'language' : 'zh-TW',
                'key' : 'AIzaSyAljxcakDVu_Cbz21iMpUx-4XPYqLGcU-U',
        }
        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?' + urllib.parse.urlencode(params)
        response = urllib.request.urlopen(url)
        reader = codecs.getreader("utf-8")
        result = json.load(reader(response))

        response_str = str()
        try:
                result_list = result['results']

                if len(result_list) >= 3 :
                        for i in range(0, 3) :
                                lng = result_list[i]['geometry']['location']['long']
                                lat = result_list[i]['geometry']['location']['lat']
                                response_str = response_str + result_list[i]['name'] + ' ( 距離'\
                                               + str(geo_distance(user_location['lng'], user_location['lat'], lng, lat))\
                                               + 'm )' + '\n' + result_list[i]['vicinity'] + '\n\n'
                else :
                        for element in result_list :
                                lng = result_list[i]['geometry']['location']['long']
                                lat = result_list[i]['geometry']['location']['lat']
                                print(distance(user_location['long'], user_location['lat'], lng, lat))
                                response_str = response_str + result_list[i]['name'] + ' ( 距離'\
                                               + str(geo_distance(user_location['long'], user_location['lat'], lng, lat))\
                                               + 'm )' + '\n' + result_list[i]['vicinity'] + '\n\n'
                return  response_str
        except:
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