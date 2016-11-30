import json
import requests
import jieba
from pprint import pprint

from django.conf import settings
from django.http import HttpResponse
from django.views import View
from dashboard.models import TextCloud
from dashboard.models import FSM
#from dashboard.models import keyword


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
                #print(message)
                greeting = ""
                cut_msg = jieba.cut(message['message']['text'])
                sender_url = 'https://graph.facebook.com/v2.6/{sender}?fields=first_name,last_name,gender&access_token={token}'.format(sender=message['sender']['id'],token=settings.FB_TOKEN)
                print (sender_url)
                sender_info = requests.get(sender_url).json()
                pprint(sender_info)
                greeting = "歡迎使用Life-all-in-one BOT \t" + sender_info['first_name']
                try:
                    search_id = FSM.objects.get(fb_id=str(message['sender']['id']))
                    greeting += "\n很高興又見到你\n"
                    search_id.state = 1
                except:
                    search_id = FSM.objects.create(fb_id=str(message['sender']['id']),first_name=sender_info['first_name'],last_name=sender_info['last_name'],gender=True,state=0)
                    greeting += "\n這是我第一次為你服務，我很榮幸\n"
                    if sender_info['gender'] == 'male':
                        search_id.gender = True
                    else:
                        search_id.gender = False
                search_id.save()
                print("="*40 + "received message:" + "="*40)
                print(cut_msg)
                print ("="*40 + "received message" + "="*40)
                cut_list = list()
                for foo in cut_msg:
                    print (foo)
                    cut_list.append(foo)
                print ("="*40 + "save objects" + "="*40)
                can_ques = ["天氣", "美食" ,"笑話", "身分證"]
                useless_dictionary = ['是','不是','你','?','.','？','。','我','的','想要']
                flag = False
                for foo in cut_list:
                    if foo in can_ques:
                        flag = True
                        break
                if flag == True:
                    for foo in cut_list:
                        if foo in useless_dictionary:
                            continue
                        try:
                            search_data = TextCloud.objects.get(text=foo)
                        except:
                            search_data = TextCloud.objects.create(text=foo, number=0,flag=True)
                        search_data.number += 1
                        search_data.save()
                        print (search_data.text)
                        print (search_data.number)
                else:
                    try:
                        search_data = TextCloud.objects.get(text=message['message']['text'])
                    except:
                        search_data = TextCloud.objects.create(text=message['message']['text'], number=0,flag=False)
                    search_data.number += 1
                    search_data.save()
                    print (search_data.text)
                    print (search_data.number)
                print ("\n")
                print ("="*40 + "req.json()" + "="*40)
                res_msg = json.dumps({"recipient": message['sender'],
                      "message": {
                          "text": greeting + ", ".join(jieba.cut(message['message']['text']))
                      }})
                req = requests.post(post_msg_url,
                                    headers={"Content-Type": "application/json"},
                                    data=res_msg)
                pprint (req.json())
        return HttpResponse(status=200)

    def get(self, request, *args, **kwargs):
        verification_code = settings.VERIFICATION_CODE
        verify_token = request.GET.get('hub.verify_token', '')
        if verification_code != verify_token:
            print (verify_toke)
            return HttpResponse(status=400)

        return HttpResponse(request.GET.get('hub.challenge', ''), status=200)