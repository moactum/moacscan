from django.core.management.base import BaseCommand, CommandError
from jingtum.models import * 

class Command(BaseCommand):
	help = 'Sychronize transactions for wallets'

	def handle(self, *args, **options):
		Transaction.objects.all().delete()
		self.stdout.write(self.style.SUCCESS('Successfully cleared transactions'))
