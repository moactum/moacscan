from celery import shared_task
import random

@shared_task
def address_determine_contract(address_pk):
	from moac.models import Address
	from django.db import transaction
	with transaction.atomic():
		address = Address.objects.select_for_update().get(pk=address_pk)
		print("\tdetermine contract {}".format(address_pk))
		address.update_code()
		#address.update_code(url='http://localhost:{}/api'.format(3000 + random.randint(0,1)))

@shared_task
def address_update_balance(address_pk):
	from moac.models import Address
	from django.db import transaction
	with transaction.atomic():
		address = Address.objects.select_for_update().get(pk=address_pk)
		print("\tupdate balance {}".format(address.display))
		address.update_balance()
		#address.update_balance(url='http://localhost:{}/api'.format(3000 + random.randint(0,1)))
