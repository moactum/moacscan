#!/usr/bin/env python

from django.db import models
from common.models import *
import re, sys, subprocess, pprint, json
from decimal import Decimal
import datetime
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
#from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone
from urllib import request
from django.utils.translation import gettext as _

class Address(TimeStampedModel):
	address = models.CharField(max_length=43,unique=True)
	display = models.CharField(max_length=24,default='')
	is_contract = models.BooleanField(_("contract?"),default=False,editable=False)
	code = models.TextField(default='',editable=False)
	balance = models.DecimalField(max_digits=18,decimal_places=9,editable=False,default=Decimal(0))
	timestamp = models.DateTimeField(blank=True,null=True,default=None,editable=False)
#	flag_balance = models.BooleanField("balance synced", default=False,editable=False)
#	balance_calculate = models.DecimalField(max_digits=18,decimal_places=9,editable=False,default=Decimal(0))
#	timestamp_calculate = models.DateTimeField(blank=True,null=True,default=None,editable=False)
#	balance_query = models.DecimalField(max_digits=18,decimal_places=9,editable=False,default=Decimal(0))
#	timestamp_query = models.DateTimeField(blank=True,null=True,default=None,editable=False)


	class Meta:
		ordering = ('address', )
		verbose_name = _('address')
		verbose_name_plural = _('addresses')

	def __str__(self):
		return self.display

	def update_display(self,force=False):
		if not self.display:
			if self.is_contract:
				self.display = "contract-%08d" % self.id
			else:
				self.display = "wallet-%08d"  % self.id
			self.save()
		elif force:
			if self.display.startswith('addr'):
				if self.is_contract:
					self.display = "contract-%08d" % self.id
				else:
					self.display = "wallet-%08d"  % self.id
				self.save()

	def update_code(self,url=''):
		if not url:
			url = "http://localhost:3003/api/address/%s/code" % self.address
		try:
			response = request.urlopen(url, timeout=30)
			if response.status == 200:
				result = json.loads(response.read().decode())
				self.code = result['code']
				if self.code and self.code != '0x':
					self.is_contract = True
				self.save()
				out = sys.stdout.write("\t... determined contract\n")
			else:
				out = sys.stdout.write("..!..http returned status %s\n" % response.status)
		except Exception as e:
			out = sys.stderr.write("... exception happend for %s/%s\n" % (self.id,index))
			print(e)
		self.update_display()

	def update_balance(self,url=''):
		if not url:
			url = "http://localhost:3003/api/address/%s" % self.address
		try:
			response = request.urlopen(url, timeout=30)
			if response.status == 200:
				result = json.loads(response.read().decode())
				self.balance = result['balance_moac']
				self.timestamp = timezone.now()
				self.save()
			else:
				out = sys.stdout.write("..!..http returned status %s\n" % response.status)
		except Exception as e:
			out = sys.stderr.write("... exception happend for %s/%s\n" % (self.id,index))
			print(e)

	def query_balance(self,url=''):
		if self.flag_balance:
			pass
		if not url:
			url = "http://localhost:3003/api/address/%s" % self.address
		try:
			response = request.urlopen(url, timeout=30)
			if response.status == 200:
				result = json.loads(response.read().decode())
				self.balance_query = result['balance_moac']
				self.timestamp_query = timezone.now()
				self.save()
				out = sys.stdout.write("... queried balance for %s\n" % (self.address))
			else:
				out = sys.stdout.write("..!..http returned status %s\n" % response.status)
		except Exception as e:
			out = sys.stderr.write("... exception happend for %s/%s\n" % (self.id,index))
			print(e)
			time.sleep(3)

class Ledger(models.Model):
	hash = models.CharField(max_length=66,unique=True)
	num_txs = models.IntegerField(default=0)
	duration = models.IntegerField(default=0)
	tps = models.IntegerField(default=0)
	difficulty = models.BigIntegerField(default=0)
	nonce = models.CharField(max_length=20,default='')
	timestamp = models.IntegerField(default=0)
	date = models.DateField(editable=False,null=True,default=None)
	miner = models.ForeignKey(Address, on_delete=models.PROTECT, editable=False,default=None, null=True, verbose_name=_('minerpool'))

	class Meta:
		ordering = ('id',)
		verbose_name = _('ledger')
		verbose_name_plural = _('ledgers')

	def __str__(self):
		return str(self.id)

	@classmethod
	def verify(cls,start=0):
		from jsonstore.models import JsonMoacLedger
		last = cls.objects.get(id=start)
		for l in cls.objects.filter(id__gt=start):
			if l.id != last.id + 1:
				print(l)
				print(last)
				return False
			if len(JsonMoacLedger.objects.get(id=l.id).data['transactions']) != l.transaction_set.count():
				print(l)
				jml = JsonMoacLedger.objects.get(id=l.id)
				l.delete()
				jml.proc_ledger()
				l = cls.objects.get(id=jml.id)
				#return False
			last = l
			if l.id % 1000 == 0:
				print(l)
		return True
class Uncle(models.Model):
	hash = models.CharField(max_length=66)
	number = models.IntegerField("hight",default=0)
	#difficulty = models.BigIntegerField(default=0)
	#nonce = models.CharField(max_length=20,default='')
	#timestamp = models.IntegerField(default=0)
	miner = models.ForeignKey(Address, on_delete=models.PROTECT, editable=False,default=None, null=True)
	ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, editable=False)

	class Meta:
		ordering = ('ledger',)
		unique_together = ('hash', 'ledger')

	def __str__(self):
		return self.hash
		#return "%s:%s" % (self.number,self.hash)

class StatLedger(models.Model):
	date = models.DateField(editable=False,unique=True)
	ledger_txs = models.ForeignKey(Ledger, on_delete=models.SET_NULL, null=True, default=None, editable=False, related_name="ledger_txs")
	ledger_tps = models.ForeignKey(Ledger, on_delete=models.SET_NULL, null=True, default=None, editable=False, related_name="ledger_tps")

class Transaction(models.Model):
	hash = models.CharField(max_length=66,primary_key=True)
	tx_from = models.ForeignKey(Address,related_name='tx_from', on_delete=models.PROTECT, editable=False, default=None, null=True)
	tx_to = models.ForeignKey(Address,related_name='tx_to', on_delete=models.PROTECT, editable=False, default=None, null=True)
	nonce = models.BigIntegerField(default=0)
	value = models.BigIntegerField("value int",default=0)
	value_moac = models.DecimalField("value",max_digits=18,decimal_places=9,editable=False,default=Decimal(0))
	index = models.IntegerField(default=0)
	ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, editable=False,default=None, null=True)

	class Meta:
		ordering = ('ledger','index')
		unique_together = ('ledger','index')

	def __str__(self):
		return self.hash
	
@receiver(pre_save, sender=Ledger)
def pre_save_ledger(sender, instance, **kwargs):
	if not instance.date:
		instance.date = timezone.make_aware(timezone.datetime.fromtimestamp(instance.timestamp)).date()

@receiver(post_save, sender=Ledger)
def post_save_ledger(sender, instance, created, **kwargs):
	if created:
		statledger,created = StatLedger.objects.get_or_create(date=instance.date)
		if not statledger.ledger_txs or statledger.ledger_txs.num_txs < instance.num_txs:
			statledger.ledger_txs = instance
			statledger.save()
		if not statledger.ledger_tps or statledger.ledger_tps.tps < instance.tps:
			statledger.ledger_tps = instance
			statledger.save()

@receiver(post_save, sender=Address)
def post_save_Address(sender, instance, created, **kwargs):
	if created:
		instance.update_code()

@receiver(pre_save, sender=Transaction)
def pre_save_transaction(sender, instance, **kwargs):
	if instance.value and not instance.value_moac:
		instance.value_moac = Decimal(instance.value) / 1000000000

