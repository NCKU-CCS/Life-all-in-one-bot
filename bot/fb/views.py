import json
import requests
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
                #response_str = certification(message['message']['text'])
                #response_str = joke()
                #current_time = entry['time']
                response_str = nearby_place({'lng':120.222874, 'lat':22.990548}, message['message']['text'])
                #response_str = restaurant({'lng':120.222874, 'lat':22.990548}, 1481200248709)
                res_msg = json.dumps({"recipient": message['sender'],
                                      "message": {
                                          "text": response_str
                                      }})
                #print (res_msg)
                req = requests.post(post_msg_url,
                                    headers={"Content-Type": "application/json"},
                                    data=res_msg)
                pprint (req.json())
        return HttpResponse(status=200)

    def get(self, request, *args, **kwargs):
        verification_code = settings.VERIFICATION_CODE
        verify_token = request.GET.get('hub.verify_token', '')
        if verification_code != verify_token:
            return HttpResponse(status=400)
	
        return HttpResponse(request.GET.get('hub.challenge', ''), status=200)



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
        clock = time.gmtime(current_time/1000).tm_hour + 8
        if clock > 24:
                clock - 24
        meal_category = str()
        if clock <= 10:
                meal_category = "早餐"
        elif clock <= 15:
                meal_category = "午餐"
        else:
                meal_category = "晚餐"
        
        lng = user_location['lng']
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
                'location': (str(user_location['lat']) + ',' + str(user_location['lng'])),
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
                                lng = result_list[i]['geometry']['location']['lng']
                                lat = result_list[i]['geometry']['location']['lat']
                                response_str = response_str + result_list[i]['name'] + ' ( 距離'\
                                               + str(geo_distance(user_location['lng'], user_location['lat'], lng, lat))\
                                               + 'm )' + '\n' + result_list[i]['vicinity'] + '\n\n'
                else :
                        for element in result_list :
                                lng = result_list[i]['geometry']['location']['lng']
                                lat = result_list[i]['geometry']['location']['lat']
                                print(distance(user_location['lng'], user_location['lat'], lng, lat))
                                response_str = response_str + result_list[i]['name'] + ' ( 距離'\
                                               + str(geo_distance(user_location['lng'], user_location['lat'], lng, lat))\
                                               + 'm )' + '\n' + result_list[i]['vicinity'] + '\n\n'
                return 	response_str	
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









