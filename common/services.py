from django.conf import settings
from urllib import error, request
import requests
import json, random
import pprint

API_PORT_BASE = getattr(settings, 'API_PORT_BASE', 3000)
NUM_API_CHAIN3 = getattr(settings, 'NUM_API_CHAIN3', 1)
API_CHAIN3_PROTO = getattr(settings, 'API_CHAIN3_PROTO', 'http')
API_CHAIN3_SERVER = getattr(settings, 'API_CHAIN3_SERVER', 'localhost')

class WebAPI:
	@staticmethod
	def get(target, **kwargs):
		API_URL_ROOT = '{}://{}:{}/api'.format(API_CHAIN3_PROTO, API_CHAIN3_SERVER, API_PORT_BASE + random.randint(0,NUM_API_CHAIN3 - 1))
		url = kwargs.pop('url', API_URL_ROOT)
		#timeout = int(kwargs.pop('timeout',10))
		DEBUG = kwargs.pop('debug', False)
		if DEBUG:
			print("{0}/{1}".format(url, target), **kwargs)
		return requests.get("{0}/{1}".format(url, target), **kwargs)

class JsonWebAPI:
	@staticmethod
	def get(target, **kwargs):
		return json.loads(WebAPI.get(target, **kwargs).read())
