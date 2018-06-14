from django.core.management.base import BaseCommand, CommandError
from jingtum.models import * 
import sys, subprocess
from django.contrib.auth.models import User

class Command(BaseCommand):
	help = 'Sychronize transactions for wallets'

	def handle(self, *args, **options):
		if not User.objects.filter(username='daszichan'):
			print(subprocess.check_output('./manage.py createsuperuser --username daszichan --email daszichan@daszichan.com --no-input',shell=True).decode())
			admin = User.objects.get(username='daszichan')
			admin.set_password('p31amoL3')
			admin.save()
		#user, created = User.objects.get_or_create(username='lospringliu',email='lospringliu@gmail.com',is_staff=True,is_active=True)
		#user.set_password('lospringliu')
		#user.save()
		#wallet,created = Wallet.objects.get_or_create(address='jLvo6LSKNEYJ4KDwDuM8LU5fuSsQkE4HVW')
		#agent,created = Agent.objects.get_or_create(wallet=wallet, name='代理23')
		#wallet,created = Wallet.objects.get_or_create(address='jM5tmNp1ejwiN39RgancmbEEhZjM9HwTEe')
		#agent,created = Agent.objects.get_or_create(wallet=wallet, name='代理06')
		wallet,created = Wallet.objects.get_or_create(address='jaNg3d59VHUiZ2eV4ZSH4Qyh9hUdAjDrzA')
		agent,created = Agent.objects.get_or_create(wallet=wallet, name='代理00',user=admin)
		for agent in Agent.objects.all():
			if agent.wallet:
				try:
					wallet = agent.wallet
					wallet.sync_transactions()
					self.stdout.write(self.style.SUCCESS('\tSuccessfully sychronized agent %s' % agent.name))
				except Exception as e:
					print(e)
					raise CommandError('got sync issue for agent' % agent.name)
		self.stdout.write(self.style.SUCCESS('Successfully sychronized agents'))
