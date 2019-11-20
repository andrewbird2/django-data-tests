from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand  # NOQA

from data_tests.models import TestMethod


class Command(BaseCommand):
    args = ""
    help = "Run data tests"

    def add_arguments(self, parser):
        parser.add_argument(
            "-m",
            "--model",
            dest="model",
            default=None
        )
        parser.add_argument(
            "-t",
            "--test",
            dest="test_method",
            default=None
        )

    def handle(self, *args, **options):
        model = options.get('model')
        test_method = options.get('test_method')
        if test_method:
            for tm in TestMethod.objects.filter(method_name=test_method):
                tm.run_test_method()
        elif model:
            qs = ContentType.objects.filter(model__iexact=model)
            if qs.count() > 1:
                raise Exception('More than one %s model exists in codebase' % model)
            model_class = qs.get().model_class()
            TestMethod.rerun_tests_for_model(model_class)
        else:
            TestMethod.rerun_all_tests()

