from django.db import models
from django.utils import timezone

# Create your models here.
class TimeStampedModel(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	changed = models.DateTimeField(default=timezone.now)
	updated = models.DateTimeField(auto_now =True)

	class Meta:
		abstract = True
