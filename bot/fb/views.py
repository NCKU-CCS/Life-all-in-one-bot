import json
import requests
import jieba
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
        pprint (msg_entries)
        post_msg_url = 'https://graph.facebook.com/v2.6/me/messages?access_token={token}'.format(token=settings.FB_TOKEN)
        for entry in msg_entries['entry']:
            for message in entry['messaging']:
                if message.get('message', '') == '':
                    continue
                if message.get('sender', '') == {'id': '409598692761944'}:#you should change the id here
                    continue
                sender_url = 'https://graph.facebook.com/v2.6/{sender}?fields=first_name,last_name,gender&access_token={token}'.format(sender=message['sender']['id'],token=settings.FB_TOKEN)
                #greeting = greetings(sender_url, message['sender']['id'])
                sender_info = requests.get(sender_url).json()
                greeting = ""
                try:
                    search_id = FSM.objects.get(fb_id=str(id))
                except:
                    search_id = FSM.objects.create(fb_id=str(id),first_name=sender_info['first_name'],last_name=sender_info['last_name'],gender=True,state=0)
                    greeting += "歡迎使用Life-all-in-one BOT \t" + sender_info['first_name'] + "\n這是我第一次為你服務，我很榮幸\n"
                    if sender_info['gender'] == 'male':
                        search_id.gender = True
                    else:
                        search_id.gender = False
                    search_id.save()
                #response_str = certification(message['message']['text'])
                #response_str = joke()
                #response_str = restaurant({'lng':120.222874, 'lat':22.990548})
                reply = ""
                if (search_id.state==2):
                    reply = location_classify()
                if (reply==""):
                    classify = msg_classify(message['message']['text'])
                    if classify=="weather":
                        pass
                    elif classify=="food":
                        pass
                    elif classify=="joke":
                        pass
                    elif classify=="cerification":
                        pass
                    elif classify=="trash":
                        reply = "hello"
                    else:
                        pass
                res_msg = json.dumps({"recipient": message['sender'],
                      "message": {
                          "text": greeting + "\n" + reply
                      }})
                req = requests.post(post_msg_url,
                                    headers={"Content-Type": "application/json"},
                                    data=res_msg)
                pprint(req.json())
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
    cut_list = list()
    for foo in cut_msg:
        print(foo)
        cut_list.append(foo)
    print("="*40 + "save objects" + "="*40)
    can_ques = {'天氣':"weather",
                '美食':"food" ,
                '笑話':"joke" ,
                '身分證':"certification",
                '健保卡':"certification",
                '駕照':"certification",
                '戶籍謄本':"certification"}
    useless_dictionary = ['是','不是','你','?','.','？','。','我','的','想要']
    category = ""
    for key in cut_list:
        if key in can_ques.keys():
            category = can_ques.get(key,"trash")
            for bar in cut_list:
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
###state=0: first man, state=1: seen before two of them are normal
# def greetings(sender_url,id):
#     sender_info = requests.get(sender_url).json()
#     greeting = "歡迎使用Life-all-in-one BOT \t" + sender_info['first_name']
#     try:
#         search_id = FSM.objects.get(fb_id=str(id))
#         greeting += "\n很高興又見到你\n"
#         search_id.state = 1
#     except:
#         search_id = FSM.objects.create(fb_id=str(id),first_name=sender_info['first_name'],last_name=sender_info['last_name'],gender=True,state=0)
#         greeting += "\n這是我第一次為你服務，我很榮幸\n"
#         if sender_info['gender'] == 'male':
#             search_id.gender = True
#         else:
#             search_id.gender = False
#     search_id.save()
#     return greeting
def location_classify(search_id,msg):
    location_detail = location(msg)
    if (location_detail=="failed"):
        search_id.state = 1
        return ""
    else:
        return restaurant(location_detail)
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


def restaurant(user_location):
	lng = user_location['lng']
	lat = user_location['lat']
	point = Point(lng, lat, srid=4326)
	restaurant_set = Restaurant.objects\
	.exclude(lng=0)\
	.annotate(distance=Distance('location', point))\
	.filter(location__distance_lte=(point, D(km=3)))\
	.order_by('distance')[:5]\

	response_str = str()
	for x in restaurant_set :
		s = x.name + "\n" + x.address + "\n\n"
		response_str = response_str + s

	return response_str
