from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework import routers, serializers, viewsets
from django.contrib.auth.models  import User
 
from jsonstore import models as jsonstore_models 
from moac import models as moac_models 
from .serializers import JsonStatSerializer, AddressSerializer, LedgerSerializer, UncleSerializer, TransactionSerializer 
 
 
# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ('url', 'username', 'email', 'is_staff')
# ViewSets define the view behavior.
class UserViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	#permission_classes = [ permissions.IsAuthenticated ]

class JsonStatViewSet(viewsets.ReadOnlyModelViewSet): 
	queryset = jsonstore_models.JsonStat.objects.all()
	serializer_class = JsonStatSerializer

class LedgerViewSet(viewsets.ReadOnlyModelViewSet): 
	queryset = moac_models.Ledger.objects.all()
	serializer_class = LedgerSerializer

class UncleViewSet(viewsets.ReadOnlyModelViewSet): 
	queryset = moac_models.Uncle.objects.all()
	serializer_class = UncleSerializer

class TransactionViewSet(viewsets.ReadOnlyModelViewSet): 
	queryset = moac_models.Transaction.objects.all()
	serializer_class = TransactionSerializer

class AddressViewSet(viewsets.ReadOnlyModelViewSet): 
	queryset = moac_models.Address.objects.order_by('-balance')
	serializer_class = AddressSerializer
