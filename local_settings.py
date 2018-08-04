import os
from datetime import timedelta
from moacscan.settings import INSTALLED_APPS, BASE_DIR, SECRET_KEY
from rest_framework.settings import api_settings

ALLOWED_HOSTS = ['*',]

INSTALLED_APPS += [
	'django.contrib.humanize',
	'django.contrib.admindocs',
	'django.contrib.postgres',
	'corsheaders',
	'rest_framework',
	#to use whitenoise, uncomment staticfiles from dasizchan.settings first
	#'whitenoise.runserver_nostatic',
	'django.contrib.staticfiles',
	'common',
	'profile',
	#'profile.apps.ProfileConfig',
	'jsonstore',
	#'jingtum',
	'moac',
	'chartit',
	#'rest_framework_simplejwt.token_blacklist',
	#'rest_framework.authtoken',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'corsheaders.middleware.CorsMiddleware',
	#'whitenoise.middleware.WhiteNoiseMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {
#	'default': {
#		'ENGINE': 'django.db.backends.sqlite3',
#		'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#	},
#	'default': {
#		'ENGINE': 'django.db.backends.mysql',
#		'NAME': 'test',								  # Or path to database file if using sqlite3.
#		'HOST': 'localhost',						  # Set to empty string for localhost. Not used with sq
#		'USER': 'root',								# Not used with sqlite3.
#		'PASSWORD': '',				  # Not used with sqlite3.
#		'PORT': '',
#		'OPTIONS': {'charset': 'utf8mb4'}
#	},
	#'dbpostgresql': {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'moacscan',								  # Or path to database file if using sqlite3.
		'HOST': '',						  # Set to empty string for localhost. Not used with sq
		'USER': '',								# Not used with sqlite3.
		'PASSWORD': '',				  # Not used with sqlite3.
		'PORT': '5432'
	}
}

#LOGIN_URL = "/accounts/login/"
#LOGOUT_URL = "/accounts/logout/"
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', 'static'))
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
STATICFILES_DIRS = (
	os.path.join(BASE_DIR, 'static'),
	)

SIMPLE_JWT = {
	'ACCESS_TOKEN_LIFETIME': timedelta(days=3),
	'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
	'ROTATE_REFRESH_TOKENS': False,
	'BLACKLIST_AFTER_ROTATION': True,

	'ALGORITHM': 'HS256',
	'SIGNING_KEY': SECRET_KEY,
	'VERIFYING_KEY': None,

	'AUTH_HEADER_TYPES': ('Bearer','JWT'),
	'USER_ID_FIELD': 'id',
	'USER_ID_CLAIM': 'user_id',

	'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
	'TOKEN_TYPE_CLAIM': 'token_type',

	'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
	'SLIDING_TOKEN_LIFETIME': timedelta(days=3),
	'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=30),
}

REST_FRAMEWORK = {
	'DEFAULT_PERMISSION_CLASSES': [
		'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
		#'rest_framework.permissions.AllowAny'
		#'rest_framework.permissions.IsAuthenticatedOrReadOnly'
		#'rest_framework.permissions.IsAuthenticated'
	],
	'DEFAULT_AUTHENTICATION_CLASSES': (
		*api_settings.defaults['DEFAULT_AUTHENTICATION_CLASSES'],
		'rest_framework_simplejwt.authentication.JWTAuthentication'
	),
	'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
	'PAGE_SIZE': 200
}
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
#CORS_ORIGIN_ALLOW_ALL = True
#CORS_ORIGIN_WHITELIST = (
#	'localhost',
#	'read.only.com',
#	'change.allowed.com',
#)
#
#CSRF_TRUSTED_ORIGINS = (
#	'localhost',
#	'change.allowed.com',
#)
#CSRF_COOKIE_NAME = 'XSRF-TOKEN'
#CSRF_HEADER_NAME = 'HTTP_X_XSRF_TOKEN'
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400
LOGIN_URL='/drf/auth/login/'
#DATABASE_ROUTERS = ['dbrouter.dbrouters.DbPostgresqlRouter',]
API_CHAIN3 = 'http://localhost:3000/api'
LOCALE_PATHS = [
	os.path.join(BASE_DIR, 'locale')
]
CELERY_BROKER_URL = 'redis://localhost:6379/9'
#DEBUG = False
DEBUG = True
