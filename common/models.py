from django.db import models
from django.utils import timezone

# Create your models here.
class TimeStampedModel(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	changed = models.DateTimeField(default=timezone.now)
	updated = models.DateTimeField(auto_now =True)

	class Meta:
		abstract = True

class TokenTopic(models.Model):
	hash = models.CharField(max_length=66,unique=True)
	class Meta:
		pass
	def __str__(self):
		return self.hash

class TokenType(models.Model):
	name = models.CharField(max_length=16,unique=True)
	class Meta:
		pass
	def __str__(self):
		return self.name
