from django.conf import settings
from urllib import error, request
import json
import pprint

DEBUG = False
API_URL_ROOT = getattr(settings, 'API_CHAIN3', 'http://localhost:3003/api')
if not API_URL_ROOT:
	API_URL_ROOT = 'http://localhost:3003/api'

class WebAPI:
	@staticmethod
	def get(target, **kwargs):
		url = kwargs.pop('url', API_URL_ROOT)
		timeout = int(kwargs.pop('timeout',10))
		if DEBUG:
			print("{0}/{1}\ttimeout={2}".format(url, target, timeout))
		return request.urlopen("{0}/{1}".format(url, target), timeout=timeout)

class JsonWebAPI:
	@staticmethod
	def get(target, **kwargs):
		if DEBUG:
			pprint.pprint(kwargs)
		return json.loads(WebAPI.get(target, **kwargs).read())
