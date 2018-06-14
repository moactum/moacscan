from django.core.management.base import BaseCommand, CommandError
from jsonstore.models import * 
import sys, subprocess
import json, pprint, datetime
import time, random
from urllib import request
from multiprocessing import Pool

from socketIO_client import SocketIO, BaseNamespace

class Namespace(BaseNamespace):
	def on_connect(self):
		sys.stdout.write("...socketio service connected\n")
	def on_message(self,msg):
		msg = msg.decode()
		try:
			if int(msg[0]) == 2:
				#pprint.pprint(msg[1:])
				msg = json.loads(msg[1:])
				if msg[0] == "ledger_closed":
					sys.stdout.write("...... syncing %s ... " % msg[1][0]['ledger_hash'])
					ledger = JsonJingtumLedger.sync(msg[1][0]['ledger_hash'])
					sys.stdout.write("synced ledger %s\n" % ledger.id)
		except Exception as e:
			sys.stdout.write("...!... got exception ...")
			e


class Command(BaseCommand):
	help = 'Sychronize json ledgers/transactions with provided ledger height and hash'

	def add_arguments(self,parser):
		parser.add_argument('--hash', action="store", dest="hash", help="specify the ledger hash, get from state.jingtum.com")
		parser.add_argument('--websocket', action="store_true", dest="websocket", help="sync ledger with websocket")
		parser.add_argument('--missing', action="store_true", dest="missing", help="sync missing ledger")
		parser.add_argument('--onceonly', action="store_true", dest="onceonly", help="syncing onestop")
		parser.add_argument('--moac', action="store_true", dest="moac", help="syncing moac ledger")

	def handle(self, *args, **options):
		if options['hash']:
			hash = options['hash']
			self.stdout.write("...got arguments to synchronize ledger from %s" % hash)
			if not options['onceonly']:
				try:
					self.stdout.write("......bypassing", ending='')
					while hash_sum:
						ledger = JsonJingtumLedger.objects.get(hash=hash)
						hash_sum = ledger.parent_hash
						self.stdout.write(" %s," % ledger.id, ending='')
				except JsonJingtumLedger.DoesNotExist:
					pass
				self.stdout.write("")
			ledger = JsonJingtumLedger.sync(hash)
			self.stdout.write("......synced ledger %s" % ledger.id)
			while not options['onceonly'] and ledger and ledger.parent_hash and ledger.id % 1000000:
				self.stdout.write("...... syncing %s ... " % ledger.parent_hash, ending='')
				if JsonJingtumLedger.objects.filter(hash_sum=ledger.parent_hash):
					self.stderr.write("...!... got earlier synced ledger, quiting")
					break
				ledger = JsonJingtumLedger.sync(ledger.parent_hash)
				self.stdout.write("synced ledger %s" % ledger.id)
		elif options['websocket']:
			self.stdout.write("...sychronize using websocket")
			while True:
				try:
					socketIO = SocketIO("state.jingtum.com", 80, Namespace)
					self.stdout.write("...started websocket synchronization")
					socketIO.wait(3600)
				except Exception as e:
					self.stderr.write("...!... got exception using websocket")
					e
					time.sleep(20)
				time.sleep(10 * random.randint(1,10))
		elif options['moac']:
			self.stdout.write("...sychronize moac ledger")
			starting = 0
			latest_ledger = JsonMoacLedger.objects.all().order_by('id').last()
			if latest_ledger:
				starting = latest_ledger.id + 1
			self.stdout.write("starting from %g" % starting)
			while True:
		#		with Pool(5) as pool:
		#			pool.map(JsonMoacLedger.sync,range(starting, 20000))
				try:
					ledger = JsonMoacLedger.sync(starting)
					starting = ledger.id + 1
					self.stdout.write("\tsyncing %s" % starting)
				except Exception as e:
					print(e)
					time.sleep(10)

		elif options['missing']:
			self.stdout.write("...sychronize missing ledgers")
			ledger = JsonJingtumLedger.objects.order_by('-id').first()
			while True:
				while ledger.id > 9292000:
					try:
						ledger = JsonJingtumLedger.objects.get(id=ledger.id - 1)
					except Exception as e:
						self.stdout.write("...syncing missing ledger at %s" % (ledger.id - 1), ending='')
						ledger = JsonJingtumLedger.sync(ledger.parent_hash)
						self.stdout.write("...synced %s" % ledger.hash_sum)
				self.stdout.write("...sychronized missing ledgers")
				self.stdout.write("... next round of syncing soon...")
				time.sleep(60 * random.randint(15,30))
		else:
			self.stdout.write("...no arguments, try to continuing syching ledger")
			ledger_starting = JsonJingtumLedger.objects.all().order_by('id').first()
			if not ledger_starting:
				self.stdout.write("......please provide initial conditions to sync ledger")
			elif ledger_starting.id == 1:
				self.stdout.write("......already synced ledger")
			elif ledger_starting.parent_hash:
				self.stdout.write("......starting sync with leger %s" % ledger_starting.parent_hash)
				ledger = JsonJingtumLedger.sync(ledger_starting.parent_hash)
				self.stdout.write("...... syncing ledger at %s" % ledger.id)
				while ledger and ledger.parent_hash:
					self.stdout.write("...... syncing %s ... " % ledger.parent_hash, ending='')
					if JsonJingtumLedger.objects.filter(hash_sum=ledger.parent_hash):
						self.stderr.write("...!... got earlier synced ledger, quiting")
						break
					ledger = JsonJingtumLedger.sync(ledger.parent_hash)
					self.stdout.write("synced ledger %s" % ledger.id)
			else:
					self.stdout.print("finished")
		self.stdout.write(self.style.SUCCESS('Successfully sychronized ledgers'))
