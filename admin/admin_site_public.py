from django.contrib import admin
from jsonstore.models import *
from moac.models import *
from django.contrib.admin.actions import delete_selected
from decimal import Decimal
import csv
from django.http import HttpResponse
from django.utils.translation import gettext as _

# Register your models here.
class JsonMoacLedgerAdmin(admin.ModelAdmin):
	list_display = ('id','data')
	def has_change_permission(self,request,obj=None):
		if obj:
			return False
		return True
	def has_module_permission(self,request):
		return True

	
class AddressAdmin(admin.ModelAdmin):
	list_display = ('display','balance','is_contract','timestamp','address')
	readonly_fields = ('address','balance','timestamp', 'display','code')
	list_filter = ('is_contract',)
	search_fields = ('=address','display')
	ordering = ('-timestamp','-balance')
	date_hierarchy = 'timestamp'

	def has_change_permission(self,request,obj=None):
		#if obj:
		#	return False
		return True
		#return request.user.is_anonymous
	def has_module_permission(self,request):
		return True

	def save_model(self, request, obj, form, change):
		pass

	def delete_model(request, obj):
		pass

class UncleAdmin(admin.ModelAdmin):
	list_display = ('ledger','number','miner','hash')
	readonly_fields = ('number','miner','ledger','hash')
	search_fields = ('=hash','=number','miner__address')
	ordering = ('-ledger__id','-number')
	date_hierarchy = 'ledger__date'

	def has_change_permission(self,request,obj=None):
		#if obj:
		#	return False
		return True
		#return request.user.is_anonymous
	def has_module_permission(self,request):
		return True

	def save_model(self, request, obj, form, change):
		pass

	def delete_model(request, obj):
		pass

class LedgerAdmin(admin.ModelAdmin):
	list_display = ('id','num_txs','tps','duration','date','miner','hash')
	readonly_fields = ('id','num_txs','tps','duration','date','timestamp','miner','hash','difficulty','nonce')
	search_fields = ('=hash','=id','miner__address')
	ordering = ('-id',)
	date_hierarchy = 'date'

	def has_change_permission(self,request,obj=None):
		#if obj:
		#	return False
		return True
		#return request.user.is_anonymous
	def has_module_permission(self,request):
		return True

	def save_model(self, request, obj, form, change):
		pass

	def delete_model(request, obj):
		pass

class TransactionAdmin(admin.ModelAdmin):
	list_display = ('ledger','tx_from','nonce','tx_to','value_moac','index','hash')
	readonly_fields = ('ledger','tx_from','tx_to','value','nonce','value_moac','index','hash')
	search_fields = ('=hash','=ledger__id','=ledger__hash','tx_from__address','tx_to__address','tx_from__display','tx_to__display')
	ordering = ('-ledger__id','-index')
	date_hierarchy = 'ledger__date'

	def has_change_permission(self,request,obj=None):
		#if obj:
		#	return False
		return True
	def has_module_permission(self,request):
		return True
	def save_model(self, request, obj, form, change):
		pass
	def delete_model(request, obj):
		pass

class AdminSite(admin.sites.AdminSite):
	site_header = _('MOACscan')
	site_title  = _('MOACscan')
	index_title = _('MOACscan')

	def has_permission(self,request):
		return True

my_admin_site_public = AdminSite(name='public')
my_admin_site_public.disable_action('delete_selected')
my_admin_site_public.register(Address,AddressAdmin)
my_admin_site_public.register(Uncle,UncleAdmin)
my_admin_site_public.register(Ledger,LedgerAdmin)
my_admin_site_public.register(Transaction,TransactionAdmin)
#my_admin_site_public.register(JsonMoacLedger,JsonMoacLedgerAdmin)
