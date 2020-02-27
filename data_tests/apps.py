from django.apps import AppConfig
from django.db.models.signals import post_migrate


def post_migration_callback(sender, **kwargs):
    from data_tests.registry import load_test_methods
    load_test_methods()

class DataTestsConfig(AppConfig):
    name = 'data_tests'
    verbose_name = 'Data tests'

    def ready(self):
        post_migrate.connect(post_migration_callback, sender=self)

