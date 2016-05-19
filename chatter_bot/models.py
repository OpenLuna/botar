from django.db import models
from bot_content.models import Person

# Create your models here.
class Location(models.Model):
	user = models.ForeignKey(Person)
	lon = models.FloatField(blank=True, null=True)
	lat = models.FloatField(blank=True, null=True)


class ChatHistory(models.Model):
	fb_id = models.CharField(max_length=32)
	text = models.CharField(max_length=256, blank=True, null=True)
	request = models.BooleanField(default=True)
	isQuestion = models.BooleanField(default=True)