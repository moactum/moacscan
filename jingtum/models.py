#!/usr/bin/env python

from django.db import models
from common.models import *
from django.contrib.auth.models import User
import re, subprocess, pprint, json
from decimal import Decimal
import datetime
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
#from mptt.models import MPTTModel, TreeForeignKey

class Ledger(models.Model):
	hash = models.CharField(max_length=66,unique=True)
	nonce = models.CharField(max_length=20,default='')
	timestamp = models.IntegerField(default=0)

	def __str__(self):
		return self.hash

class Transaction(models.Model):
	hash = models.CharField(max_length=66,primary_key=True)
	nonce = models.BigIntegerField(default=0)
	index = models.IntegerField(default=0)
	ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, editable=False,default=None, null=True)

	class Meta:
		pass

	def __str__(self):
		return self.hash

#class Currency(models.Model):
#	name = models.CharField(max_length=64,)
#	issuer = models.CharField(max_length=64,default='',editable=False,)
#
#	class Meta:
#		verbose_name = '通证'
#		verbose_name_plural = '通证'
#		ordering = ('name', )
#		unique_together = ('name', 'issuer')
#
#	def __str__(self):
#		return self.name
#	
#class Result(models.Model):
#	name = models.CharField(max_length=16,unique=True,)
#
#	def __str__(self):
#		return self.name
#
#
#class Direction(models.Model):
#	name = models.CharField(max_length=16,unique=True)
#
#	def __str__(self):
#		return self.name
#
#
#class Wallet(models.Model):
#	address = models.CharField(max_length=128,unique=True,)
#	secret = models.CharField(max_length=128,blank=True,default='',)
#
#	class Meta:
#		ordering = ('address', )
#
#	def __str__(self):
#		#return "%s***%s" % (self.address[:5], self.address[-5:])
#		return self.address
#
#	def sync_transactions(self, leger_limit=8000000, page_limit=2000, datetime_limit=datetime.datetime(2017,12,1)):
#		pass
#	#	marker = {}
#	#	results_per_page = 200
#	#	page = 1
#	#	has_more = True
#	#	num_trans = 0
#	#	num_exists = 0
#	#	#ledger_limit = 8000000
#	#	#page_limit = 2000
#
#	#	if not self.agent_set.all():
#	#		raise ValueError("no agent associated")
#	#	agent = self.agent_set.all().first()
#
#	#	while has_more and page < page_limit:
#	#		num_trans = 0
#	#		num_exists = 0
#	#		if 'ledger' in marker.keys():
#	#			out = json.loads(subprocess.check_output("http --timeout 120 'https://api.jingtum.com/v2/accounts/%s/transactions?results_per_page=%s&marker={ledger:%s,seq:%s}'" % (self.address, results_per_page, marker['ledger'], marker['seq']),shell=True).decode())
#	#		else:
#	#			out = json.loads(subprocess.check_output("http --timeout 120 'https://api.jingtum.com/v2/accounts/%s/transactions?results_per_page=%s'" % (self.address, results_per_page),shell=True).decode())
#	#		if 'marker' in out.keys():
#	#			marker = out['marker']
#	#		else:
#	#			marker = {}
#	#			has_more = False
#	#		if 'transactions' not in out.keys():
#	#			has_more = False
#	#			break
#	#		else:
#	#			if len(out['transactions']) < results_per_page:
#	#				has_more = False
#	#		transactions = list(filter(lambda x: 'counterparty' in x.keys() and 'type' in x.keys() and (x['type'] == 'sent' or x['type'] == 'received') and 'result' in x.keys() and 'amount' in x.keys() and 'memos' in x.keys() and type(x['amount']) == type({}) and x['result'] == 'tesSUCCESS' and 'currency' in x['amount'].keys() and 'issuer' in x['amount'].keys() and ((x['amount']['currency'] == 'CNY' and x['amount']['issuer'] == 'jGa9J9TkqtBcUoHe2zqhVFFbgUVED6o9or')), out['transactions']))
#	#		#transactions = list(filter(lambda x: 'counterparty' in x.keys() and 'type' in x.keys() and 'result' in x.keys() and 'amount' in x.keys() and 'memos' in x.keys() and type(x['amount']) == type({}) and x['result'] == 'tesSUCCESS' and 'currency' in x['amount'].keys() and 'issuer' in x['amount'].keys() and (x['amount']['currency'] == 'SWT' or (x['amount']['currency'] == 'CNY' and x['amount']['issuer'] == 'jGa9J9TkqtBcUoHe2zqhVFFbgUVED6o9or')), out['transactions']))
#	#		for transaction in transactions:
#	#			num_trans += 1
#	#			if datetime.datetime.fromtimestamp(transaction['date']) < datetime_limit:
#	#				has_more = False
#	#				break
#	#			print("%s\t%s" % (transaction['hash'], transaction['memos']))
#	#			trans, created = Transaction.objects.get_or_create(hash_sum=transaction['hash'])
#	#			if created:
#	#				trans.agent = agent
#	#				currency, created = Currency.objects.get_or_create(name=transaction['amount']['currency'], issuer=transaction['amount']['issuer'])
#	#				counterparty, created = Wallet.objects.get_or_create(address=transaction['counterparty'])
#	#				result, created = Result.objects.get_or_create(name=transaction['result'])
#	#				direction, created = Direction.objects.get_or_create(name=transaction['type'])
#	#				trans.currency = currency
#	#				trans.amount = Decimal(transaction['amount']['value'])
#	#				trans.counterparty = counterparty
#	#				trans.date_int = transaction['date']
#	#				trans.memos = re.sub(r',', ' ', ' '.join(transaction['memos'])[:128])
#	#				trans.result = result
#	#				trans.direction = direction
#	#				trans.save()
#	#			else:
#	#				num_exists += 1
#	#		if num_trans > 10 and num_exists == num_trans:
#	#			has_more = False
#	#		page += 1
#
#	def sync_balances(self):
#		pass
#
#
#
#
#class Agent(models.Model):
#	name = models.CharField(max_length=32,unique=True,)
#	wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True,blank=True,default=None)
#	user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True,blank=True,default=None)
#
#	class Meta:
#		verbose_name = '代理'
#		verbose_name_plural = '代理'
#		ordering = ('name', )
#
#	def __str__(self):
#		return self.name
#
#
##	currency = models.ForeignKey(Currency,verbose_name="通证",on_delete=models.PROTECT,editable=False,default=None,null=True)
##	amount = models.DecimalField("数额",max_digits=20,decimal_places=8,editable=False,default=Decimal(0))
##	counterparty = models.ForeignKey(Wallet, verbose_name="对家", on_delete=models.PROTECT,null=True,default=None,editable=False,)
##	date_int = models.IntegerField(default=0,editable=False)
##	date = models.DateField(editable=False,null=True)
##	memos = models.CharField("留言", max_length=128,blank=True,default='',)
##	result = models.ForeignKey(Result,on_delete=models.PROTECT,editable=False,default=None,null=True)
##	direction = models.ForeignKey(Direction, verbose_name="类型", on_delete=models.PROTECT, null=True, editable=False,default=None)
##	deposite = models.BooleanField(verbose_name='充值',default=False,)
##	lock_deposite = models.BooleanField(default=False,editable=False,)
##	withdraw = models.BooleanField(verbose_name='回血',default=False,)
##	lock_withdraw = models.BooleanField(default=False,editable=False,)
##	activation = models.BooleanField(verbose_name='激活',default=False,editable=False,)
##	agent = models.ForeignKey(Agent,verbose_name='代理', on_delete=models.PROTECT,editable=False,default=None, null=True)
#
##@receiver(pre_save, sender=Transaction)
##def pre_save_transaction(sender, instance, **kwargs):
##	if instance.date_int:
##		if not instance.date:
##			instance.date = datetime.datetime.fromtimestamp(instance.date_int).date()
##	if not instance.lock_deposite:
##		if instance.currency and instance.currency.name == 'CNY' and re.match('.*D[0-9]{15}', instance.memos, re.I):
##			instance.lock_deposite = True
##			instance.deposite = True
##	if not instance.lock_withdraw:
##		if instance.direction and instance.direction.name == 'received' and instance.currency and instance.currency.name == 'CNY' and instance.counterparty and (instance.counterparty.address == 'jaNg3d59VHUiZ2eV4ZSH4Qyh9hUdAjDrzA' or instance.counterparty.address == 'jU2YgNfRcTghKJXWTTWNMBpPnmXhyihEpn' ):
##			if 'c2c' == instance.memos or (instance.amount == Decimal(400000) or instance.amount == Decimal(500000) or instance.amount == Decimal(50000)):
##				instance.lock_withdraw = True
##				instance.withdraw = True
