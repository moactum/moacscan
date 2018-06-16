"""moacscan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.urls import include, path
	2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import permissions
from rest_framework.documentation import include_docs_urls
from django.urls import include, path, re_path
#from admin.admin_site import my_admin_site
from admin.admin_site_public import my_admin_site_public
from django.conf.urls.i18n import i18n_patterns

#from rest_framework_simplejwt.views import (
#	TokenObtainPairView,
#	TokenVerifyView,
#	TokenRefreshView,
#)
from .views import homepage, live
from . import apiviews

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
#router.register(r'users', apiviews.UserViewSet)
router.register(r'jsonstats', apiviews.JsonStatViewSet)
router.register(r'address', apiviews.AddressViewSet)
router.register(r'block', apiviews.LedgerViewSet)
router.register(r'uncle', apiviews.UncleViewSet)
router.register(r'tx', apiviews.TransactionViewSet)

urlpatterns = [
	re_path('^$', homepage, name='home'),
	path('live/', live, name='live'),
	path('admin/doc/', include('django.contrib.admindocs.urls')),
	path('admin/', admin.site.urls),
	path('public/', my_admin_site_public.urls),
#	path('drf/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#	path('drf/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
#	path('drf/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#	path('drf/auth/', include('rest_framework.urls', namespace='rest_framework')),
	path('drf/', include(router.urls)),
	path('api-docs/', include_docs_urls(title='Superbook API')),
]
