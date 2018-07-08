#!/usr/bin/env python

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.db.models import Sum, Count, Max, Min
#from mptt.models import MPTTModel, TreeForeignKey
from urllib import error, request
import sys, random, time, json, re
from decimal import Decimal
from common.models import *
import common
from moac.models import Token, Ledger, Address, Transaction, Uncle

#hashrate_tera = pow(2,40)
hashrate_tera = 1e12
hashrate_average_sample = 10
coinmarket_update_minimum = 60
class JsonStat(models.Model):
	metric = models.CharField(max_length=16,unique=True)
	data = JSONField(default={})
	timestamp = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.metric

	def update(self):
		if self.metric == 'coinmarket':
			if (timezone.now() - self.timestamp).seconds > coinmarket_update_minimum:
				try:
					r = common.WebAPI.get('ticker/moac/', url='https://api.coinmarketcap.com/v1/',timeout=20)
					if r.status == 200:
						data = json.loads(r.read())
						data[0]['price_btc'] = int( float(data[0]['price_btc']) * 1000000 ) / 1000000
						self.data = data
						self.save()
				except Exception as e:
					print(e)
		elif self.metric == 'ledger':
			self.data['ledgers'] = Ledger.objects.count()
			self.data['uncles'] = Uncle.objects.count()
			self.data['moac_mined'] = 2 * (self.data['ledgers'] + self.data['uncles'])
			self.data['moac_circulation'] = int(Address.objects.aggregate(Sum('balance'))['balance__sum'])
			self.data['uncle_ratio'] = int(100 * self.data['uncles'] / self.data['ledgers'])
			self.data['wallets_apponly'] = Address.objects.filter(app_only=True).count()
			self.data['wallets_mainnet'] = Address.objects.filter(app_only=False).filter(is_contract=False).count()
			self.data['wallets'] = self.data['wallets_apponly'] + self.data['wallets_mainnet']
			self.data['contracts'] = Address.objects.filter(is_contract=True).count()
			self.data['tokens'] = Token.objects.count()
			self.data['transactions'] = Transaction.objects.count()
			self.data['subchains'] = TokenType.objects.count()
			if self.data['ledgers'] > 100:
				self.data['difficulty'] = 10 * Ledger.objects.get(id=self.data['ledgers'] - 1).difficulty // hashrate_tera / 10
				self.data['bigpools'] = Address.objects.annotate(Count('ledger')).filter(ledger__count__gt=10000).count()
				self.data['hashrate'] = 10 * Ledger.objects.filter(id__gte=self.data['ledgers'] - hashrate_average_sample).filter(id__lt=self.data['ledgers']).aggregate(Sum('difficulty'))['difficulty__sum'] // hashrate_tera // (Ledger.objects.get(id=self.data['ledgers'] - 1).timestamp - Ledger.objects.get(id=self.data['ledgers'] - hashrate_average_sample - 1).timestamp) / 10
			else:
				self.data['difficulty'] = 0
				self.data['bigpools'] = 0
				self.data['hashrate'] = 0
			self.save()
		else:
			pass

class JsonJingtumLedger(models.Model):
	hash = models.CharField(max_length=64,unique=True,editable=False)
	parent_hash = models.CharField(max_length=64,default='',unique=True,editable=False)
	data = JSONField()
	synced = models.BooleanField(default=False, editable=False)

	def __str__(self):
		return "%s: %s" % (self.id, self.hash)

	@classmethod
	def sync(cls,hash):
		done = False
		try:
			ledger = cls.objects.get(hash=hash)
			done = True
		except cls.DoesNotExist:
			pass
		while not done:
			try:
				response = common.WebAPI.get("query/ledger/{}".format(hash), url='http://state.jingtum.com/',timeout=90)
				if response.status == 200:
					result = json.loads(response.read().decode())
					summary = result['data']['data']['summary']
					parent_hash = summary['parent_hash']
					ledger = cls(id=int(summary['ledger_index']),hash=hash,parent_hash=parent_hash,data=result)
					ledger.save()
					done = True
				else:
					out = sys.stdout.write("..!..http returned status %s\n" % response.status)
					time.sleep(10 * random.randint(1,10))
			except Exception as e:
				out = sys.stderr.write("exception happend\n")
				print(e)
				time.sleep(60 * random.randint(1,10))
		return ledger

class JsonMoacLedger(models.Model):
	hash = models.CharField(max_length=66,unique=True,editable=False)
	parent_hash = models.CharField(max_length=66,default='',unique=True,editable=False)
	data = JSONField()
	synced = models.BooleanField(default=False, editable=False)

	class Meta:
		ordering = ('id',)
	def __str__(self):
		return "%s: %s" % (self.id, self.hash)

	def delete(self):
		for l in Ledger.objects.filter(id=self.id):
			l.delete()
		super(JsonMoacLedger,self).delete()

	def sync_uncles(self):
		if self.synced:
			return True
		if self.data['uncles']:
			for index in range(len(self.data['uncles'])):
				sys.stdout.write("\t...trying %s/%s\n" % (self.id,index))
				try:
					response = common.WebAPI.get("uncle/{0}/{1}".format(self.id,index))
					if response.status == 200:
						result = json.loads(response.read().decode())
						hash = result['hash']
						uncle = JsonMoacUncle(hash=hash,ledger=self,data=result)
						uncle.save()
						out = sys.stdout.write("... retrieved uncle for %s/%s\n" % (self.id,index))
					else:
						out = sys.stdout.write("..!..http returned status %s\n" % response.status)
						return False
				except Exception as e:
					out = sys.stderr.write("... exception happend for %s/%s\n" % (self.id,index))
					print(e)
					return False
		self.synced = True
		self.save()
		sys.stdout.write("\t...synced uncles\n")
		return True

	def proc_ledger(self,do_uncle=False, bypass_balance=False):
		addresses = set()
		ledger_new = False
		try:
			ledger = Ledger.objects.get(hash=self.hash)
			if do_uncle:
				for uncle_hash in self.data['uncles']:
					uncle,created = Uncle.objects.get_or_create(hash=uncle_hash,ledger=ledger)
					jmu = JsonMoacUncle.objects.get(hash=uncle_hash,ledger=JsonMoacLedger.objects.get(hash=ledger.hash))
					miner,created = Address.objects.get_or_create(address=jmu.data['miner'])
					if created and ledger.timestamp:
						miner.created = timezone.make_aware(timezone.datetime.fromtimestamp(ledger.timestamp))
						miner.app_only = False
						miner.save()
					if miner.app_only:
						miner.app_only = False
						miner.save()
					addresses.add(miner)
					uncle.miner = miner
					uncle.number = jmu.data['number']
					uncle.save()
		except Ledger.DoesNotExist:
			miner,created = Address.objects.get_or_create(address=self.data['miner'])
			addresses.add(miner)
			timestamp=self.data['timestamp']
			if self.id == 0:
				timestamp = 1525064660
				if created:
					miner.created = timezone.make_aware(timezone.datetime.fromtimestamp(timestamp))
					miner.app_only = False
					miner.save()
				if miner.app_only:
					miner.app_only = False
					miner.save()
				ledger = Ledger(hash=self.hash, id=self.id, difficulty = self.data['difficulty'], nonce = self.data['nonce'], miner=miner, timestamp=timestamp)
				ledger.save()
			else:
				if created:
					miner.created = timezone.make_aware(timezone.datetime.fromtimestamp(timestamp))
					miner.app_only = False
					miner.save()
				if miner.app_only:
					miner.app_only = False
					miner.save()
				ledger_new = True
				duration = int(timestamp - Ledger.objects.get(id=self.id -1).timestamp)
				num_txs = len(self.data['transactions'])
				tps = int(num_txs / duration)
				ledger = Ledger(hash=self.hash, id=self.id, num_txs=num_txs, tps=tps, duration=duration, difficulty = self.data['difficulty'], nonce = self.data['nonce'], miner=miner, timestamp=timestamp)
				ledger.save()
				if self.data['transactions']:
					sys.stdout.write('update transactions:\n\t...')
					for txr in self.data['transactions']:
						sys.stdout.write("%s, " % txr['transactionIndex'])
						tx_from, created = Address.objects.get_or_create(address=txr['from'])
						if created:
							tx_from.created = timezone.make_aware(timezone.datetime.fromtimestamp(timestamp))
							tx_from.app_only = False
							tx_from.save()
						if tx_from.app_only:
							tx_from.app_only = False
							tx_from.save()
						addresses.add(tx_from)
						if txr['to']:
							tx_to, created = Address.objects.get_or_create(address=txr['to'])
							if created:
								tx_to.created = timezone.make_aware(timezone.datetime.fromtimestamp(timestamp))
								tx_to.app_only = False
								tx_to.save()
							if tx_to.app_only:
								tx_to.app_only = False
								tx_to.save()
							addresses.add(tx_to)
						else:
							tx_to = None
						transaction, created = Transaction.objects.get_or_create(ledger=ledger,hash=txr['hash'],tx_from=tx_from, nonce=txr['nonce'], tx_to=tx_to, value=int(float(txr['value'])) / 1000000000, index=int(txr['transactionIndex']))
						transaction.save()
					sys.stdout.write('\n')
				for uncle_hash in self.data['uncles']:
					uncle,created = Uncle.objects.get_or_create(hash=uncle_hash,ledger=ledger)
					jmu = JsonMoacUncle.objects.get(hash=uncle_hash,ledger=JsonMoacLedger.objects.get(hash=ledger.hash))
					miner,created = Address.objects.get_or_create(address=jmu.data['miner'])
					if created:
						miner.created = timezone.make_aware(timezone.datetime.fromtimestamp(jmu.data['timestamp']))
						miner.app_only = False
						miner.save()
					if miner.app_only:
						miner.app_only = False
						miner.save()
					addresses.add(miner)
					uncle.miner = miner
					uncle.number = jmu.data['number']
					uncle.save()
			if not bypass_balance:
				sys.stdout.write('update balances:\n\t...')
				for address in list(filter(lambda x: not x.is_contract and not x.app_only and not re.match(r'^0x00000000',x.address, re.I), addresses)):
					a = Address.objects.get(address=address.address)
					sys.stdout.write("%s, " % a.display)
					a.update_balance()
				sys.stdout.write('\n')
			if ledger_new:
				jsl,created = JsonStat.objects.get_or_create(metric='ledger')
				jsl.update()
				jsc,created = JsonStat.objects.get_or_create(metric='coinmarket')
				jsc.update()
			
	@classmethod
	def verify(cls,start=0):
		last = cls.objects.get(id=start)
		for jml in cls.objects.filter(id__gt=start):
			if jml.parent_hash != last.hash:
				print(jml)
				print(last)
				if last.id != jml.id - 1:
					print("\t...trying to sync missing ledgers")
					id_to_sync = last.id + 1
					while id_to_sync < jml.id:
						cls.sync(id_to_sync)
						id_to_sync += 1
				else:
					print("\tparent:%s" % jml.parent_hash)
					print("\tparent:%s" % last.hash)
			last = jml
		return True

	@classmethod
	def sync(cls,height):
		done = False
		last = None
		ledger = None
		try:
			if height > 0:
				last = cls.objects.get(id=height-1)
			ledger = cls.objects.get(id=height)
			done = True
			if last and ledger.parent_hash != last.hash:
				sys.stdout.write("\tinconsistancy found, delete last two\n")
				last.delete()
				ledger.delete()
				if height > 1:
					ledger = cls.objects.get(id=height-2)
		except cls.DoesNotExist:
			pass
		while not done:
			try:
				response = common.WebAPI.get("block/{0}".format(height))
				if response.status == 200:
					result = json.loads(response.read().decode())
					hash = result['hash']
					parent_hash = result['parentHash']
					if height > 0 and last and parent_hash == last.hash:
						ledger = cls(id=height,hash=hash,parent_hash=parent_hash,data=result)
						ledger.save()
					elif height == 0:
						ledger = cls(id=height,hash=hash,parent_hash=parent_hash,data=result)
						ledger.save()
					else:
						sys.stdout.write("\tinconsistancy found, delete last two\n")
						if last:
							last.delete()
						if height > 1:
							ledger = cls.objects.get(id=height-2)
					done = True
				else:
					out = sys.stdout.write("..!..http returned status %s\n" % response.status)
					time.sleep(random.randint(5,10))
			except Exception as e:
				out = sys.stderr.write("exception happend\n")
				print(e)
				time.sleep(random.randint(5,10))
		sys.stdout.write("\tsynced %s" % height)
		return ledger

class JsonMoacUncle(models.Model):
	hash = models.CharField(max_length=66,editable=False)
	data = JSONField()
	synced = models.BooleanField(default=False, editable=False)
	ledger = models.ForeignKey(JsonMoacLedger, on_delete=models.CASCADE)

	class Meta:
		ordering = ('ledger',)
		unique_together = ('hash','ledger')
	def __str__(self):
		return "%s: %s" % (self.ledger.id, self.hash)

	def delete(self):
		for u in Uncle.objects.filter(hash=self.hash):
			u.delete()
		super(JsonMoacUncle,self).delete()

class JsonTokenLog(models.Model):
	block_number = models.IntegerField(default=0)
	tx_index = models.IntegerField(default=0)
	log_index = models.IntegerField(default=0)
	data = JSONField(default={})

	class Meta:
		unique_together = ('block_number','tx_index','log_index')
	def __str__(self):
		return "{}-{}-{}".format(self.block_number, self.tx_index, self.log_index)

@receiver(pre_save, sender=JsonJingtumLedger)
def pre_save_ledger_jingtum(sender, instance, **kwargs):
	pass

@receiver(pre_save, sender=JsonMoacLedger)
def pre_save_ledger_moac(sender, instance, **kwargs):
	pass

@receiver(post_save, sender=JsonMoacLedger)
def post_save_ledger_moac(sender, instance, created, **kwargs):
	if created:
		# retrieve JsonMoacUncles
		instance.sync_uncles()
		# generate ledgers, transactions and uncles
		#instance.proc_ledger(bypass_balance=True)
		instance.proc_ledger()

