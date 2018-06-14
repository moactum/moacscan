from django.apps import AppConfig


class ProfileConfig(AppConfig):
	name = 'profile'
	verbose_name = 'User Profile'

	def ready(self):
		from . import signals
