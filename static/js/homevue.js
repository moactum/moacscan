function addMessage(list, msg) {
	list.unshift(msg.data.block);
	$('#message-list').parent().animate({
		scrollTop: $('#message-list').height()
	}, 1000);
}
function addTxs(list, msg) {
	msg.data.block.transactions.forEach( tx => list.unshift(tx) );
	$('#tx-list').parent().animate({
		scrollTop: $('#tx-list').height()
	}, 1000);
}
function addStat(list, msg) {
	list.unshift(msg.data.info_stat);
}

$(function () {
	var vmMessageList = new Vue({
		el: '#scrollbar2',
		data: {
			messages: []
		},
		methods: {
			block: function (msg) {
				window.open(`/api/block/${msg.hash}`);
			}
		}
	});
	window.vmMessageList = vmMessageList;
	var vmTxList = new Vue({
		el: '#scrollbar',
		data: {
			txs: []
		},
		methods: {
			transaction: function (tx) {
				window.open(`/api/tx/${tx}`);
			},
		}
	});
	window.vmTxList = vmTxList;
	var vmJsonStat = new Vue({
		el: '#jsonstat',
		data: {
			info_stat: []
		}
	});
	window.vmJsonStat = vmJsonStat;

	var ws_conncted = true;

	ws.onmessage = function(event) {
		var data = event.data;
		var msg = JSON.parse(data);
		if (msg.type === 'datafeed') {
			if (msg.data.block) {
				addMessage(vmMessageList.messages, msg);
				addTxs(vmTxList.txs, msg);
			}
			if (msg.data.info_stat) {
				addStat(vmJsonStat.info_stat, msg);
			}
		}
	};
	ws.onclose = function (evt) {
		console.log('[closed] ' + evt.code);
		ws_connected = false;
	};
	ws.onerror = function (code, msg) {
		console.log('[ERROR] ' + code + ': ' + msg);
		ws_connected = false;
	};

});
