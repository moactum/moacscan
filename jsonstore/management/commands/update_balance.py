from django.core.management.base import BaseCommand, CommandError
import time
from moac.models import Address

class Command(BaseCommand):
	help = 'offload sync_ledger to update moac balance here'

	def handle(self, *args, **options):
		self.stdout.write("...update moac balances")
		while True:
			for address in Address.objects.filter(flag_balance=True).order_by('-updated'):
				address.update_balance()
				self.stdout.write(self.style.SUCCESS('\t... updated {}'.format(address.display)))
			self.stdout.write(self.style.SUCCESS('updated moac balances'))
			time.sleep(5)
