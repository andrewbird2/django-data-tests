# -*- coding: utf-8
from django.apps import AppConfig


class DataTestsConfig(AppConfig):
    name = 'data_tests'

    def ready(self):
        from .registry import populate_test_methods
        populate_test_methods()
