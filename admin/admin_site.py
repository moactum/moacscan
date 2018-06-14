from django.contrib import admin
from jingtum.models import *
from django.contrib.admin.actions import delete_selected
from decimal import Decimal
import csv
from django.http import HttpResponse

# Register your models here.
#class AgentAdmin(admin.ModelAdmin):
#	list_display = ('name','wallet','user')
#	actions = ['sync_transactions','export_deposite']
#
#	def has_change_permission(self,request,obj=None):
#		return request.user.is_active and (not obj or request.user.is_superuser)
#	def has_module_permission(self,request):
#		return request.user.is_active
#	
#	def get_queryset(self,request):
#		qs = super().get_queryset(request)
#		if request.user.is_superuser:
#			return qs
#		else:
#			return qs.filter(user=request.user)
#
#	def sync_transactions(self,request,queryset):
#		for obj in queryset:
#			if obj.user == request.user:
#				self.message_user(request,"开始同步 %s 充值记录" % (obj.wallet.address))
#				obj.wallet.sync_transactions()
#				self.message_user(request,"同步完毕 %s, 可前往查看" % obj.wallet.address)
#			elif request.user.is_superuser:
#				self.message_user(request,"开始同步 %s 充值记录" % (obj.wallet.address))
#				obj.sync_transactions()
#				self.message_user(request,"同步完毕 %s, 可前往查看" % obj.wallet.address)
#			else:
#				self.message_user(request, "没有权限同步 %s" % obj.wallet.address)
#
#	sync_transactions.short_description = "同步所选代理的充值记录"
#
#	def export_deposite(self,request,queryset):
#		response = HttpResponse(content_type='text/csv')
#		response['Content-Disposition'] = 'attachment; filename="records.csv"'
#		writer = csv.writer(response)
#		for obj in queryset:
#			for record in obj.transaction_set.filter(deposite=True):
#				writer.writerow([record.date.isoformat(), str(float(record.amount)), record.counterparty.address, record.hash_sum, record.memos])
#		return response
#	export_deposite.short_description = "导出充值记录"
#
#class TransactionAdmin(admin.ModelAdmin):
#	list_display = ('hash_sum',)
#	#list_display = ('date','amount','counterparty','deposite','withdraw','memos')
#	#list_editable = ('deposite','withdraw','memos')
#	#list_filter = ('deposite','withdraw','direction','agent')
#	##list_filter = ('deposite','withdraw','direction','counterparty__agent')
#	##list_filter = ('deposite','withdraw','currency',)
#	#date_hierarchy = 'date'
#	#actions = ['summarize_amount','export_deposite']
#	#list_max_show_all = 20000
#	#save_on_top = True
#
#	def has_change_permission(self,request,obj=None):
#		return request.user.is_active and ( not obj or obj and (obj.agent == request.user.agent or request.user.is_superuser))
#	def has_module_permission(self,request):
#		return request.user.is_active
#
#	def get_queryset(self,request):
#		qs = super().get_queryset(request)
#		if request.user.is_superuser:
#			return qs
#		else:
#			if request.user.agent:
#				return qs.filter(agent=request.user.agent)
#			else:
#				return qs.none()
#
#	def export_deposite(self,request,queryset):
#		response = HttpResponse(content_type='text/csv')
#		response['Content-Disposition'] = 'attachment; filename="records.csv"'
#		writer = csv.writer(response)
#		for record in queryset:
#			writer.writerow([record.date.isoformat(), str(float(record.amount)), record.counterparty.address, record.hash_sum, record.memos])
#		return response
#	export_deposite.short_description = "导出所选记录"
#
#	def summarize_amount(self,request,queryset):
#		total = Decimal(0)
#		for obj in queryset:
#			if obj.direction.name == 'sent':
#				total -= obj.amount
#			elif obj.direction.name == 'received':
#				total += obj.amount
#			else:
#				pass
#		self.message_user(request,"total amount: %s" % total)
#
#	summarize_amount.short_description = "计算所选 交易纪录金额"
#
#class AdminSite(admin.sites.AdminSite):
#	site_header = '充值回血'
#	site_title  = '充值回血'
#	index_title = '充值回血'
#
#	def has_permission(self,request):
#		return request.user.is_active
#
#my_admin_site = AdminSite(name='daili')
#my_admin_site.disable_action('delete_selected')
#my_admin_site.register(Transaction,TransactionAdmin)
#my_admin_site.register(Agent,AgentAdmin)
#
