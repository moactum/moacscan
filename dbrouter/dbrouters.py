class DbPostgresqlRouter:

	def db_for_read(self, model, **hints):
		if model._meta.app_label == 'jsonstore':
			return 'dbpostgresql'
		return None

	def db_for_write(self, model, **hints):
		if model._meta.app_label == 'jsonstore':
			return 'dbpostgresql'
		return None

	def allow_relation(self, obj1, obj2, **hints):
		if obj1._meta.app_label == 'jsonstore' and obj2._meta.app_label == 'jsonstore':
			return True
		elif obj1._meta.app_label == 'jsonstore' or obj2._meta.app_label == 'jsonstore':
			return False
		else:
			return None

	def allow_migrate(self, db, app_label, model_name=None, **hints):
		if app_label == 'jsonstore':
			return db == 'dbpostgresql'
		return None
		
