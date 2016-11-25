from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TextCloud
import json
# Create your views here.
class GetTextCloud(APIView):
	def get(self, request):
		true_search = TextCloud.objects.filter(flag=True)
		true_list = list()
		for foo in true_search:
			tmp = {
				"count": foo.number,
				"keyword": foo.text,
			}
			true_list.append(tmp)
		false_search = TextCloud.objects.filter(flag=False)
		false_list = list()
		for foo in false_search:
			tmp = {
				"count": foo.number,
				"keyword": foo.text,
			}
			false_list.append(tmp)
		req_data = json.dumps({"most": true_list, "lack": false_list})
		return Response(req_data, status=status.HTTP_200_OK)