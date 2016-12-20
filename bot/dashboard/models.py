from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
# Create your models here.

class TextCloud(models.Model):
    text = models.CharField(max_length=320, default='non_data')
    number = models.IntegerField()
    flag = models.BooleanField()

    def __str__(self):
        return self.text

class FSM(models.Model):
	fb_id = models.CharField(max_length=320, default='non_data')
	first_name = models.CharField(max_length=320, default='non_data')
	last_name = models.CharField(max_length=320, default='non_data')
	gender = models.BooleanField()
	state = models.IntegerField(default=0)
	lng = models.FloatField(default=0.0)
	lat = models.FloatField(default=0.0)
	location = models.PointField(geography=True, srid=4326, default='SRID=3857;POINT(0.0 0.0)')
	def __str__(self):
		return self.user_id
