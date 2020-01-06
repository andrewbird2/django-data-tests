# -*- coding: utf-8
from django.apps import AppConfig


class DataTestsConfig(AppConfig):
    name = 'data_tests'
    verbose_name = 'Data tests'

    def ready(self):
        from data_tests.registry import load_test_methods
        load_test_methods()
