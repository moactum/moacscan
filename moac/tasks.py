from celery import shared_task

@shared_task
def address_update_balance(address_id):
	from moac.models import Address
	address = Address.objects.get(id=address_id)
	print("\tin celery update address {}".format(address.display))
	address.update_balance()
