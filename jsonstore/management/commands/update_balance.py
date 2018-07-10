from django.core.management.base import BaseCommand, CommandError
import time, multiprocessing
from moac.models import Address

class Command(BaseCommand):
	help = 'offload sync_ledger to update moac balance here'

	def handle(self, *args, **options):
		self.stdout.write("...update moac balances")
		def update_balance(address):
			self.stdout.write(self.style.SUCCESS('\t... updating {} ...'.format(address.display)))
			address.update_balance()
		while True:
			with multiprocessing.Pool(3) as pool:
				list(map(update_balance, Address.objects.filter(flag_balance=True).order_by('-updated')))
			self.stdout.write(self.style.SUCCESS('updated moac balances'))
			time.sleep(5)
