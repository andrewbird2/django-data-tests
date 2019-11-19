import inspect

from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from data_tests.models import TestMethod


def populate_test_methods():
    for cls in apps.get_models():
        for name, method in inspect.getmembers(cls):
            if getattr(method, 'is_data_test', False):
                content_type = ContentType.objects.get_for_model(cls)
                tm, created = TestMethod.objects.update_or_create(
                    content_type=content_type,
                    method_name=method.__name__,
                    defaults={
                        'title': method.model_test_title or method.__name__.replace('_', ' ').capitalize(),
                        'is_class_method': method.is_class_method
                    }
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
