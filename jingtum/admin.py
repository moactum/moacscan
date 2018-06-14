from django.contrib import admin
from .models import *
from decimal import Decimal

# Register your models here.
#@admin.register(Currency)
#class CurrencyAdmin(admin.ModelAdmin):
#	list_display = ('name','issuer')
#
#@admin.register(Agent)
#class AgentAdmin(admin.ModelAdmin):
#	list_display = ('name','wallet','user')
#
#@admin.register(Transaction)
#class TransactionAdmin(admin.ModelAdmin):
#	list_display = ('hash_sum',)
#	#list_display = ('direction','amount','currency','date','counterparty','deposite','withdraw','memos')
#	#list_editable = ('deposite','withdraw')
#	#list_filter = ('currency','deposite','withdraw','direction','agent',)
#	#list_filter = ('deposite','withdraw','direction','counterparty__agent')
#	#list_filter = ('deposite','withdraw','currency',)
#	#date_hierarchy = 'date'
#	#actions = ['summarize_amount']
#	list_max_show_all = 20000
#
#	#def summarize_amount(self,request,queryset):
#	#	total = Decimal(0)
#	#	for obj in queryset:
#	#		if obj.direction.name == 'sent':
#	#			total -= obj.amount
#	#		elif obj.direction.name == 'received':
#	#			total += obj.amount
#	#		else:
#	#			pass
#	#	self.message_user(request,"total amount: %s" % total)
#
#	#summarize_amount.short_description = "计算所选 交易纪录金额"
#
