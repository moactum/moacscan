from django.db import models
from django.conf import settings
from common.models import *

# Create your models here.

class Profile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
