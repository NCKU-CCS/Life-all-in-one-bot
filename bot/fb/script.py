import json

from fb.models import Joke
from fb.models import Eat

#with open('/home/mini/djangogirls/Life-all-in-one-bot/bot/fb/joke.json') as data_file:
#	json_data = json.load(data_file)

#for element in json_data:
#	joke = Joke(title=element['title'], context=element['context'])
#	joke.save()

with open('/home/mini/djangogirls/Life-all-in-one-bot/bot/fb/台南-東區.json') as data_file:
	json_data = json.load(data_file)

for element in json_data:
	eat = Eat(category=element['category'], name=element['name'], address=element['address'], link=element['link'])
	eat.save()



