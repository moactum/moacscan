from django.core.management.base import BaseCommand, CommandError
from jsonstore.models import * 
import sys, subprocess
import json, pprint, datetime
import time, random
from urllib import request
import multiprocessing

class Command(BaseCommand):
	help = 'Sychronize token related staff'

	def add_arguments(self,parser):
		parser.add_argument('--hash', action="store", dest="hash", help="specify the ledger hash, get from state.jingtum.com")
		parser.add_argument('--moac', action="store_true", dest="moac", help="syncing moac ledger")

	def handle(self, *args, **options):
		self.stdout.write("...sychronize moac tokens")
		def sync_token(jtl):
			self.stdout.write(self.style.SUCCESS('\t... updating {} ...'.format(jtl.__str__())))
			jtl.update_token_log()
		with multiprocessing.Pool(5) as pool:
			list(map(sync_token, JsonTokenLog.objects.filter(synced=False)))
	#	while True:
	#		#with Pool(5) as pool:
	#		#	pool.map(JsonMoacLedger.sync,range(starting, 20000))
	#		try:
	#			for jtl in JsonTokenLog.objects.filter(synced=False):
	#				jtl.update_token_log()
	#		except Exception as e:
	#			self.stdout.write(e.__str__())
		self.stdout.write(self.style.SUCCESS('sychronized tokens'))
	#		time.sleep(3600)
