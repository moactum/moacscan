from celery import shared_task
#from django.db import transaction

@shared_task
def json_token_log_sync():
	from jsonstore.models import JsonTokenLog
	print("\tasync celery tokenlog sync")
	JsonTokenLog.sync()
