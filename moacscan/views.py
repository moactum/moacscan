import os
from chartit import DataPool, Chart
from jsonstore.models import JsonStat
from moac.models import *
from django.shortcuts import render_to_response
from django.db.models import F, Sum, Avg, Count


def homepage(_):
	#NUM_LATEST = 5
	stat_ledger,created = JsonStat.objects.get_or_create(id=1,metric='ledger')
	stat_coinmarket,created = JsonStat.objects.get_or_create(id=2,metric='coinmarket')
	ds_ledger = DataPool(
		series=[
		{
			'options': { 
				'source': StatLedger.objects.order_by('date')
				#'source': OrgCount.objects.filter(date__gte=timezone.datetime(2017,11,1),org__name='ibmcom')
			},
			'terms': [
				{'date': 'date'},
				{'Daily Max of Txs': 'ledger_txs__num_txs'}
			]
		},
		{
			'options': {
				'source': StatLedger.objects.order_by('date')
			},
			'terms': [
				{'date': 'date'},
				{'Daily Max of Tps': 'ledger_tps__tps'}
			]
		},
		]
	)

	ds_balance = DataPool(
		series=[
		{
			'options': {
				'source': Address.objects.order_by('-balance')[:50]
				#'source': OrgCount.objects.filter(date__gte=timezone.datetime(2017,11,1),org__name='ibmcom')
			},
			'terms': [
				'address',
				'balance'
			]
		}
		]
	)

	cht_ledger = Chart(
		datasource=ds_ledger,
		series_options=[
		{
			'options': {
				'type': 'line',
				'stacking': False,
				'yAxis': 0,
			},
			'terms': {
				'date': [
					'Daily Max of Txs',
					],
			}
		},
		{
			'options': {
				'type': 'line',
				'stacking': False,
				'yAxis': 1,
			},
			'terms': {
				'date': [
					'Daily Max of Tps',
					],
			}
		},
		],

		chart_options={
			'title': {
				'text': 'daily block statistic: max TXS (left y) and max TPS(right y)'
			},
			'xAxis':
				{
				'type': 'date',
				'tickInterval': 1,
				'title': {
					'text': ' '
					}
				},
			'yAxis': [
				{
				'title': {
					'text': 'Number Of Transactions',
				},
				'min': 0
				},
				{
				'title': {
					'text': 'Transactions Per Second',
				},
				'min': 0,
				'opposite': True
				},
			],
			'chart': {
				'zoomType': 'x',
			},
			},
		)

	cht_balance = Chart(
		datasource=ds_balance,
		series_options=[
		{
			'options': {
				'type': 'pie',
				'stacking': False,
			},
			'terms': {
				'address': [
					'balance',
					],
			}
		}
		],
		chart_options={
			'title': {
				'text': 'Token Distribution top 50'
			}
			},
		)

	return render_to_response('index.html', {'chart_list': [ cht_ledger, cht_balance ], 'stat_ledger': stat_ledger, 'stat_coinmarket': stat_coinmarket})

def live(_):
	#NUM_LATEST = 5
	stat_ledger = JsonStat.objects.get(metric='ledger')
	stat_coinmarket = JsonStat.objects.get(metric='coinmarket')

	return render_to_response('live.html', {'stat_ledger': stat_ledger, 'stat_coinmarket': stat_coinmarket})

