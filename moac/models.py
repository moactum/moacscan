#!/usr/bin/env python

from django.db import models, transaction
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

class ShardingFlag(models.Model):
	flag = models.CharField(max_length=16,unique=True)

	class Meta:
		pass

	def __str__(self):
		return self.flag

class Address(TimeStampedModel):
	address = models.CharField(max_length=43,primary_key=True)
	display = models.CharField(max_length=24,default='')
	is_contract = models.BooleanField(_("contract?"),default=False,editable=False)
	code = models.TextField(default='',editable=False)
	balance = models.DecimalField(max_digits=18,decimal_places=9,editable=False,default=Decimal(0))
	app_only = models.BooleanField(default=True,editable=False)
	#flag_balance = models.BooleanField(default=False,editable=False)

	class Meta:
		ordering = ('address', )
		verbose_name = _('address')
		verbose_name_plural = _('addresses')

	def __str__(self):
		return self.address

	def update_display(self,force=False):
		if not self.display or force:
			if self.is_contract:
				self.display = "contract-{}".format(self.address[:8])
			else:
				self.display = "wallet-{}".format(self.address[:8])
			self.save()

	def update_code(self,url=None):
		try:
			if self.address.startswith('0x0000000000000000'):
				return
			if not url:
				response = common.WebAPI.get("address/{}/code".format(self.address))
			else:
				response = common.WebAPI.get("address/{}/code".format(self.address), url=url)
			if response.ok:
				result = response.json()
				code = result['code']
				if code and code != '0x':
					self.is_contract = True
					self.save()
					self.update_erc20_token()
			#	else:
			#		stataddress,created = StatAddress.objects.get_or_create(date=timezone.now().date())
			#		if self.app_only:
			#			stataddress.apponly += 1
			#		else:
			#			stataddress.wallet += 1
			#		stataddress.total = Address.objects.filter(is_contract=False).count()
			#		stataddress.save()
			#	#out = sys.stdout.write("\t... determined contract\n")
			else:
				out = sys.stdout.write("..!..http returned error status\n")
			#	stataddress,created = StatAddress.objects.get_or_create(date=timezone.now().date())
			#	if self.app_only:
			#		stataddress.apponly += 1
			#	else:
			#		stataddress.wallet += 1
			#	stataddress.total = Address.objects.filter(is_contract=False).count()
			#	stataddress.save()
		except Exception as e:
			out = sys.stderr.write("... exception happend for %s\n" % (self.address))
		#	stataddress,created = StatAddress.objects.get_or_create(date=timezone.now().date())
		#	if self.app_only:
		#		stataddress.apponly += 1
		#	else:
		#		stataddress.wallet += 1
		#	stataddress.total = Address.objects.filter(is_contract=False).count()
		#	stataddress.save()
			print(e)
		if not self.display:
			self.update_display()

	def update_changed(self):
		last_tx = Transaction.objects.filter(Q(tx_from=self) | Q(tx_to=self)).last()
		if last_tx:
			self.changed = timezone.make_aware(timezone.datetime.fromtimestamp(last_tx.block.timestamp))
		self.save()

	def update_erc20_token(self,url=None):
		token_type = None
		try:
			if not url:
				response = common.WebAPI.get("address/{}/token".format(self.address))
			else:
				response = common.WebAPI.get("address/{}/token".format(self.address), url=url)
			if response.ok:
				result = response.json()
				if "protocol" in result.keys():
					token_type,created = TokenType.objects.get_or_create(name=result["protocol"])
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
				out = sys.stdout.write("..!..http returned error status\n")
		except Exception as e:
			out = sys.stderr.write("... exception happend for %s\n" % (self.address))
			print(e)

	def update_balance(self,url=None):
		try:
			if not url:
				response = common.WebAPI.get("address/{}/balance".format(self.address))
			else:
				response = common.WebAPI.get("address/{}/balance".format(self.address), url=url)
			if response.ok:
				result = response.json()
				self.balance = result['balance_moac']
				last_tx = Transaction.objects.filter(Q(tx_from=self) | Q(tx_to=self)).last()
				if last_tx:
					self.changed = timezone.make_aware(timezone.datetime.fromtimestamp(last_tx.block.timestamp))
				self.save()
			else:
				out = sys.stdout.write("..!..http returned error status\n")
		except Exception as e:
			out = sys.stderr.write("... exception happend for %s\n" % (self.address))
			print(e)

class Block(models.Model):
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
		verbose_name = _('block')
		verbose_name_plural = _('block')

	def __str__(self):
		return str(self.id)

	@classmethod
	def verify(cls,start=0):
		from jsonstore.models import JsonMoacBlock
		last = cls.objects.get(id=start)
		for l in cls.objects.filter(id__gt=start):
			if l.id != last.id + 1:
				print(l)
				print(last)
				return False
			if len(JsonMoacBlock.objects.get(id=l.id).data['transactions']) != l.transaction_set.count():
				print(l)
				jml = JsonMoacBlock.objects.get(id=l.id)
				l.delete()
				jml.proc_block()
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
	block = models.ForeignKey(Block, on_delete=models.CASCADE, editable=False)

	class Meta:
		ordering = ('block',)
		unique_together = ('hash', 'block')

	def __str__(self):
		return self.hash
		#return "%s:%s" % (self.number,self.hash)

class Token(TimeStampedModel):
	symbol = models.CharField(max_length=32,db_index=True)
	name = models.CharField(max_length=64,default='token name')
	decimals = models.IntegerField(default=0)
	token_type = models.ForeignKey(TokenType,on_delete=models.SET_NULL,null=True,default=None,editable=False)
	total_supply = models.DecimalField(max_digits=30,decimal_places=2,editable=False,default=Decimal(0))
	address = models.OneToOneField(Address,null=True,default=None,on_delete=models.SET_NULL,editable=False)
	owners = models.ManyToManyField(Address,related_name='owners',editable=False)
	class Meta:
		unique_together = ('symbol', 'token_type', 'address')
	def __str__(self):
		return self.symbol

class StatLedger(models.Model):
	date = models.DateField(editable=False,unique=True)
	block_txs = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True, default=None, editable=False, related_name="block_txs")
	block_tps = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True, default=None, editable=False, related_name="block_tps")

class StatAddress(models.Model):
	date = models.DateField(editable=False,unique=True)
	apponly = models.IntegerField(default=0,editable=False)
	wallet = models.IntegerField(default=0,editable=False)
	total = models.IntegerField(default=0,editable=False)

class Transaction(models.Model):
	hash = models.CharField(max_length=66,primary_key=True)
	tx_from = models.ForeignKey(Address,related_name='tx_from', on_delete=models.PROTECT, editable=False, default=None, null=True)
	tx_to = models.ForeignKey(Address,related_name='tx_to', on_delete=models.PROTECT, editable=False, default=None, null=True)
	nonce = models.BigIntegerField(default=0)
	value = models.BigIntegerField("value int",default=0)
	value_moac = models.DecimalField("value",max_digits=18,decimal_places=9,editable=False,default=Decimal(0))
	index = models.IntegerField(default=0)
	#sharding = models.ForeignKey(ShardingFlag, on_delete=models.PROTECT, editable=False,default=None, null=True)
	block = models.ForeignKey(Block, on_delete=models.CASCADE, editable=False,default=None, null=True)

	class Meta:
		ordering = ('block','index')
		unique_together = ('block','index')

	def __str__(self):
		return self.hash
	
class TokenLog(TimeStampedModel):
	block = models.ForeignKey(Block, on_delete=models.CASCADE, editable=False)
	transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, editable=False)
	index = models.IntegerField(default=0)
	topic = models.ForeignKey(TokenTopic, on_delete=models.CASCADE, null=True, default=None, editable=False)
	address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, default=None, editable = False)
	wallets = models.ManyToManyField(Address, related_name='wallets')

	class Meta:
		ordering = ('-block','-transaction','-index')
		unique_together = ('block','transaction','index')
	def __str__(self):
		return "{}-{}-{}".format(self.block.id,self.transaction.index,self.index)

@receiver(pre_save, sender=Block)
def pre_save_block(sender, instance, **kwargs):
	if not instance.date:
		instance.date = timezone.make_aware(timezone.datetime.fromtimestamp(instance.timestamp)).date()

@receiver(post_save, sender=Block)
def post_save_block(sender, instance, created, **kwargs):
	if created:
		statblock,created = StatLedger.objects.get_or_create(date=instance.date)
		if not statblock.block_txs or statblock.block_txs.num_txs < instance.num_txs:
			statblock.block_txs = instance
			statblock.save()
		if not statblock.block_tps or statblock.block_tps.tps < instance.tps:
			statblock.block_tps = instance
			statblock.save()

#@receiver(post_save, sender=Address)
#def post_save_Address(sender, instance, created, **kwargs):
#	if created:
#		with transaction.atomic():
#			instance = Address.objects.select_for_update().get(id=instance.id)
#			instance.update_code()
##		#tasks.address_update_contract.delay(instance.id)

@receiver(pre_save, sender=Transaction)
def pre_save_transaction(sender, instance, **kwargs):
	if instance.value and not instance.value_moac:
		instance.value_moac = Decimal(instance.value) / 1000000000

