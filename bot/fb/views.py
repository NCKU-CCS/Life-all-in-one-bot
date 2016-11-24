import json
import requests
import jieba
from pprint import pprint

from django.conf import settings
from django.http import HttpResponse
from django.views import View
from dashboard.models import TextCloud
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
                #init_msg = message['message']['text'];
                cut_msg = jieba.cut(message['message']['text'])
                # print("="*40 + "received message:" + "="*40)
                # print(cut_msg)
                res_msg = json.dumps({"recipient": message['sender'],
                                      "message": {
                                          "text": ", ".join(jieba.cut(message['message']['text']))
                                      }})
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

                for foo in cut_list:
                    if foo in useless_dictionary:
                        continue
                    try:
                        search_data = TextCloud.objects.get(text=foo)
                    except:
                        search_data = TextCloud.objects.create(text=foo, number=0,flag=flag)
                    search_data.number += 1
                    search_data.save()
                    print (search_data.text)
                    print (search_data.number)
                    print("="*40)
                print ("\n")
                print ("="*40 + "req.json()" + "="*40)
                req = requests.post(post_msg_url,
                                    headers={"Content-Type": "application/json"},
                                    data=res_msg)
                pprint (req.json())
        return HttpResponse(status=200)

    def get(self, request, *args, **kwargs):
        verification_code = settings.VERIFICATION_CODE
        #verification_code = "kuoteng"
        verify_token = request.GET.get('hub.verify_token', '')
        #print (verification_code)
        #print (verify_toke)
        if verification_code != verify_token:
            print (verify_toke)
            return HttpResponse(status=400)

        return HttpResponse(request.GET.get('hub.challenge', ''), status=200)