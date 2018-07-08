#!/usr/bin/env python

from django.db import models
from common.models import *
import common
import re, sys, subprocess, pprint, json
from decimal import Decimal
import datetime
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
#from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone
from urllib import request
from django.db.models import Q
from django.utils.translation import gettext as _

class TokenType(models.Model):
	name = models.CharField(max_length=16,unique=True)
	class Meta:
		pass
	def __str__(self):
		return self.name

class Address(TimeStampedModel):
	address = models.CharField(max_length=43,unique=True)
	display = models.CharField(max_length=24,default='')
	is_contract = models.BooleanField(_("contract?"),default=False,editable=False)
	app_only = models.BooleanField(default=True,editable=False)
	code = models.TextField(default='',editable=False)
	balance = models.DecimalField(max_digits=18,decimal_places=9,editable=False,default=Decimal(0))

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

	def update_code(self,url=None):
		try:
			if not url:
				response = common.WebAPI.get("address/{}/code".format(self.address))
			else:
				response = common.WebAPI.get("address/{}/code".format(self.address), url=url)
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
			out = sys.stderr.write("... exception happend for %s\n" % (self.address))
			print(e)
		self.update_display()

	def update_changed(self):
		last_tx = Transaction.objects.filter(Q(tx_from=self) | Q(tx_to=self)).last()
		if last_tx:
			self.changed = timezone.make_aware(timezone.datetime.fromtimestamp(last_tx.ledger.timestamp))
		self.save()

	def update_erc20_token(self,url=None):
		token_type,created = TokenType.objects.get_or_create(name='erc20')
		try:
			if not url:
				response = common.WebAPI.get("token/{}".format(self.address))
			else:
				response = common.WebAPI.get("token/{}".format(self.address), url=url)
			if response.status == 200:
				result = json.loads(response.read().decode())
				pprint.pprint(result)
				token,created = Token.objects.get_or_create(symbol=result['symbol'], token_type=token_type, address=self)
				if created:
					token.created = self.created
					token.save()
				token.name = result['name']
				token.decimals = int(result['decimals'])
				token.total_supply = Decimal(result['totalSupply'])
				token.save()
			else:
				out = sys.stdout.write("..!..http returned status %s\n" % response.status)
		except Exception as e:
			out = sys.stderr.write("... exception happend for %s\n" % (self.address))
			print(e)

	def update_balance(self,url=None):
		try:
			if not url:
				response = common.WebAPI.get("address/{}".format(self.address))
			else:
				response = common.WebAPI.get("address/{}".format(self.address), url=url)
			if response.status == 200:
				result = json.loads(response.read().decode())
				self.balance = result['balance_moac']
				last_tx = Transaction.objects.filter(Q(tx_from=self) | Q(tx_to=self)).last()
				if last_tx:
					self.changed = timezone.make_aware(timezone.datetime.fromtimestamp(last_tx.ledger.timestamp))
				self.save()
			else:
				out = sys.stdout.write("..!..http returned status %s\n" % response.status)
		except Exception as e:
			out = sys.stderr.write("... exception happend for %s\n" % (self.address))
			print(e)

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

class Token(TimeStampedModel):
	symbol = models.CharField(max_length=8,db_index=True)
	name = models.CharField(max_length=32,default='token name')
	decimals = models.IntegerField(default=0)
	token_type = models.ForeignKey(TokenType,on_delete=models.PROTECT,editable=False)
	total_supply = models.DecimalField(max_digits=30,decimal_places=2,editable=False,default=Decimal(0))
	address = models.OneToOneField(Address,null=True,default=None,on_delete=models.SET_NULL,editable=False)
	owners = models.ManyToManyField(Address,related_name='owners',editable=False)
	class Meta:
		unique_together = ('symbol', 'token_type', 'address')
	def __str__(self):
		return self.symbol

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

