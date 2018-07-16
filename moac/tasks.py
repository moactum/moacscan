from celery import shared_task

@shared_task
def address_update_balance(address_id):
	from moac.models import Address
	from django.db import transaction
	with transaction.atomic():
		address = Address.objects.select_for_update().get(id=address_id)
		print("\tin celery update address {}".format(address.display))
		address.update_balance()