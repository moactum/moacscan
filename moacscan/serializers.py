from rest_framework import serializers 
from jsonstore import models as jsonstore_models
from moac import models as moac_models
 
 
class JsonStatSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = jsonstore_models.JsonStat
		fields = ("id","metric", "timestamp","data")
class BlockSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = moac_models.Block
		fields = ('__all__')
class UncleSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = moac_models.Uncle
		fields = ('__all__')
class TransactionSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = moac_models.Transaction
		fields = ('__all__')
class AddressSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = moac_models.Address
		fields = ("address", "display", "is_contract", "balance", "updated")
