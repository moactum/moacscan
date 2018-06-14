from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework import routers, serializers, viewsets
from django.contrib.auth.models  import User
 
from jsonstore import models as jsonstore_models 
from .serializers import JsonStatSerializer 
 
 
# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ('url', 'username', 'email', 'is_staff')
# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	#permission_classes = [ permissions.IsAuthenticated ]

class JsonStatViewSet(viewsets.ModelViewSet): 
	queryset = jsonstore_models.JsonStat.objects.all()
	serializer_class = JsonStatSerializer
