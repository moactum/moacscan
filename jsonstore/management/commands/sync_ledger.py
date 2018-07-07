from django.core.management.base import BaseCommand, CommandError
from jsonstore.models import * 
import sys, subprocess
import json, pprint, datetime
import time, random
from urllib import request
from multiprocessing import Pool

#from socketIO_client import SocketIO, BaseNamespace

class Command(BaseCommand):
	help = 'Sychronize json ledgers/transactions with provided ledger height and hash'

	def add_arguments(self,parser):
		parser.add_argument('--hash', action="store", dest="hash", help="specify the ledger hash, get from state.jingtum.com")
		parser.add_argument('--websocket', action="store_true", dest="websocket", help="sync ledger with websocket")
		parser.add_argument('--missing', action="store_true", dest="missing", help="sync missing ledger")
		parser.add_argument('--moac', action="store_true", dest="moac", help="syncing moac ledger")

	def handle(self, *args, **options):
		self.stdout.write("...sychronize moac ledger")
		starting = 0
		latest_ledger = JsonMoacLedger.objects.all().order_by('id').last()
		if latest_ledger:
			starting = latest_ledger.id + 1
		self.stdout.write("starting from %g" % starting)
		while True:
			#with Pool(5) as pool:
			#	pool.map(JsonMoacLedger.sync,range(starting, 20000))
			try:
				ledger = JsonMoacLedger.sync(starting)
				starting = ledger.id + 1
				self.stdout.write("\tsyncing %s" % starting)
			except Exception as e:
				print(e)
				time.sleep(10)
		self.stdout.write(self.style.SUCCESS('Successfully sychronized ledgers'))
