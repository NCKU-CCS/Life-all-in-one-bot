import json
import codecs
import urllib
import urllib.request
import os

from fb.models import Joke
from fb.models import Restaurant
from django.contrib.gis.geos import Point

def address_to_coordinates(address) :
	params = {
		'address': address,
		'sensor' : 'false',
	}
	url = 'http://maps.google.com/maps/api/geocode/json?' + urllib.parse.urlencode(params)
	response = urllib.request.urlopen(url)
	reader = codecs.getreader("utf-8")
	result = json.load(reader(response))
	x = 0
	try:
		return result['results'][0]['geometry']['location']
	except:
		print(result)
		return {'lng': 0.0, 'lat': 0.0}

with open(os.path.join('.','fb','joke.json')) as data_file:
	json_data = json.load(data_file)

for element in json_data:
	joke = Joke(title=element['title'], context=element['context'])
	joke.save()

with open(os.path.join('.','fb','台南-東區.json')) as data_file:
	json_data = json.load(data_file)

for element in json_data:
	coordinates = address_to_coordinates(element['address'])
	restaurant = Restaurant(
		name = element['name'],
		address = element['address'],
		link = element['link'],
		category = element['category'],
		lng = coordinates['lng'],
		lat = coordinates['lat'],
		location = Point(float(coordinates['lng']), float(coordinates['lat']))
	)
	restaurant.save()













