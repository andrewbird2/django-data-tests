from collections import defaultdict
import inspect

from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from data_tests.models import TestMethod

registry = defaultdict(dict)

def load_test_methods():
    for model in apps.get_models():
        content_type = ContentType.objects.get_for_model(model)
        for name, method in inspect.getmembers(model):
            if getattr(method, 'is_data_test', False):
                registry[content_type][method.__name__] = {
                    'title': method.model_test_title or
                             method.__name__.replace('_', ' ').capitalize(),
                    'is_class_method': method.is_class_method
                }


def add_test_methods_to_database():
    for content_type, method_dict in registry.items():
        for method_name, defaults in method_dict.items():
            TestMethod.objects.update_or_create(
                content_type=content_type,
                method_name=method_name,
                defaults=defaults
            )

# Used as a decorator
def test_method(title=None, is_class_method=False):
    def test_method_inner(method):
        method.is_data_test = True
        method.is_class_method = is_class_method
        method.model_test_title = title
        return method

    return test_method_inner


def test_class_method(title=None):
    return test_method(title, is_class_method=True)
