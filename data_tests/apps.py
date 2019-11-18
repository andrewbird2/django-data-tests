# -*- coding: utf-8
from django.apps import AppConfig


class ValidatedConfig(AppConfig):
    name = 'validated'

    def ready(self):
        from .registry import populate_test_methods
        populate_test_methods()
