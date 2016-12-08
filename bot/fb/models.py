from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

class Joke(models.Model):
	title = models.TextField()
	context = models.TextField()

class Restaurant(models.Model):
	name = models.TextField()
	address = models.TextField()
	link = models.TextField()
	category = ArrayField(
		models.TextField(),
		size = 3,
	)
	lng = models.FloatField()
	lat = models.FloatField()
	location = models.PointField(geography=True, srid=4326)

	#def save(self, **kwargs):
	#	self.loaction = Point(float(self.lng), float(self.lat))
	#	super(Restaurant, self).save(**kwargs)

