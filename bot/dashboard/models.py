from django.db import models
# Create your models here.
# class keyword(models.Model):
# 	text = models.CharField(max_length=320)

class TextCloud(models.Model):
    text = models.CharField(max_length=320, default='non_data')
    number = models.IntegerField()
    flag = models.BooleanField()

    def __str__(self):
        return self.text