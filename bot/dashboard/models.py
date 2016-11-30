from django.db import models
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
	state = models.IntegerField()
	def __str__(self):
		return self.user_id
