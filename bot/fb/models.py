from django.db import models

class Joke(models.Model):
	title = models.TextField()
	context = models.TextField()

class Eat(models.Model):
	category = models.TextField()
	name = models.TextField()
	address = models.TextField()
	link = models.TextField()
