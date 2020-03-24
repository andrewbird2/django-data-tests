# -*- coding: utf-8 -*-

from functools import lru_cache
import logging

from django.apps import apps
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models, router
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel

from data_tests.constants import MAX_MESSAGE_LENGTH

logger = logging.getLogger(__name__)

db_for_read = lru_cache()(router.db_for_read)


@python_2_unicode_compatible
class TestMethod(models.Model):
    class Meta:
        unique_together = ('content_type', 'method_name')

    title = models.CharField(max_length=256)
    method_name = models.CharField(max_length=256)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='test_methods')
    is_class_method = models.BooleanField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        return super(TestMethod, self).save(*args, **kwargs)

    def model_class(self):
        return self.content_type.model_class()

    def method(self):
        return getattr(self.model_class(), self.method_name)

    def delete_stale_results(self):
        deleted, _ = self.test_results.filter(object_id__isnull=True).delete()
        if deleted:
            logger.info('Deleted {} stale test results'.format(deleted))

    def add_new_result_objects(self):
        all_object_pks = set(self.model_class().objects.values_list('pk', flat=True))
        existing_test_results = set(self.test_results.values_list('object_id', flat=True))
        to_insert = []
        for new_id in all_object_pks - existing_test_results:
            to_insert.append(TestResult(test_method=self, content_type=self.content_type, object_id=new_id))

        TestResult.objects.bulk_create(to_insert)

    def _run_test_method_instance(self):
        for result in self.test_results.all():
            result.run_test_method()

    def class_method_result(self):
        assert self.is_class_method
        results = getattr(self.model_class(), self.method_name)()
        if type(results) is tuple:
            failing, message = results
        else:
            failing = results
            message = None

        return failing, message

    def _run_test_method_class(self):
        try:
            qs_failing, message = self.class_method_result()

            # Update failing results
            self.test_results.filter(object_id__in=qs_failing.values_list('id', flat=True)).update(passed=False,
                                                                                                   message=message or '')
            # Update passing results
            self.test_results.exclude(object_id__in=qs_failing.values_list('id', flat=True)).update(passed=True,
                                                                                                    message='')

        except Exception as e:
            self.test_results.update(passed=False, message="Test failed to run correctly! {}".format(str(e)))

    def run_test_method(self):
        logger.info('Running test: {} {}'.format(self.content_type, self))
        self.delete_stale_results()
        self.add_new_result_objects()
        if self.is_class_method:
            self._run_test_method_class()
        else:
            self._run_test_method_instance()

        results = self.test_results.all()
        logger.info('Test completed: {} successful, {} failing (of which {} are supposed to fail)\n'.format(
            results.filter(passed=True).count(),
            results.filter(passed=False).count(),
            results.filter(passed=False, xfail=True).count()
        ))

    @classmethod
    def rerun_tests_for_model(cls, model):
        ct = ContentType.objects.get(app_label=model._meta.app_label, model=model._meta.model_name)
        for test_method in cls.objects.filter(content_type=ct):
            test_method.run_test_method()

    @classmethod
    def rerun_all_tests(cls):
        for test_method in cls.objects.all():
            test_method.run_test_method()

    @classmethod
    def add_test_methods_for_content_type(cls, content_type):
        from data_tests.registry import test_methods
        method_dicts = filter(lambda x: x['content_type'] == content_type, test_methods)
        should_exist = set([x['method_name'] for x in method_dicts])
        does_exist = set([x.method_name for x in cls.objects.filter(content_type=content_type)])

        if should_exist - does_exist:
            for method_name in should_exist - does_exist:
                dict = list(filter(lambda x: x['method_name'] == method_name, test_methods))[0]
                test_method, created = cls.objects.update_or_create(**dict)
                assert created


@python_2_unicode_compatible
class TestResult(TimeStampedModel):
    test_method = models.ForeignKey(TestMethod, on_delete=models.CASCADE, related_name='test_results')
    message = models.CharField(max_length=MAX_MESSAGE_LENGTH)
    passed = models.BooleanField(default=False)
    xfail = models.BooleanField(default=False, verbose_name="Supposed to fail")
    justification = models.CharField(blank=True, max_length=500)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='test_results')
    object_id = models.PositiveIntegerField(blank=True, null=True, db_index=True)

    def __str__(self):
        return str(self.test_method)

    class Meta:
        unique_together = ('test_method', 'object_id', 'content_type')

    @staticmethod
    @lru_cache()
    def get_model_class_from_content_type(content_type_id):
        """ cached version of self.content_type.model_class() """
        ct = ContentType.objects.get(id=content_type_id)
        return apps.get_model(ct.app_label, ct.model)

    def get_object(self):
        """ return the object that was tested """
        model_class = self.get_model_class_from_content_type(self.content_type_id)
        db_alias = db_for_read(model_class)
        manager = model_class._base_manager.using(db_alias)
        return manager.get(pk=self.object_id)

    @classmethod
    def get_test_results(cls, obj=None, qs=None):
        assert obj is not None or qs is not None  # Note "assert obj or qs" does not work
        ids = [obj.id] if obj else qs.values_list('id', flat=True)
        class_type = type(obj) if obj else qs.model
        ct = ContentType.objects.get(app_label=class_type._meta.app_label, model=class_type._meta.model_name)
        return cls.objects.filter(content_type=ct, object_id__in=ids)

    def run_test_method(self):
        try:
            obj = self.get_object()
            method = self.test_method.method()
            if self.test_method.is_class_method:
                qs_failing, message = self.test_method.class_method_result()
                if obj in qs_failing:
                    method_result = False, message
                else:
                    method_result = True
            else:
                method_result = method(obj)
        except Exception as e:
            method_result = False, "Test failed to run correctly! {}".format(str(e))

        if type(method_result) is bool:
            self.passed = method_result
            self.message = ''
        else:
            passed, message = method_result
            self.passed = passed
            self.message = message[0:MAX_MESSAGE_LENGTH] if message else ''

        self.save()

    def object_admin_url(self):
        return reverse("admin:%s_%s_change" % (self.content_type.app_label, self.content_type.model),
                       args=(self.object_id,))

    def object_admin_hyperlink(self, text=None):
        return '<a href="%s">%s</a>' % (self.object_admin_url(), text or str(self))

    def test_result_admin_url(self):
        model = self._meta.model
        ct = ContentType.objects.get(app_label=model._meta.app_label, model=model._meta.model_name)
        return reverse("admin:%s_%s_change" % (ct.app_label, ct.model), args=(self.id,))

    def test_result_admin_hyperlink(self, text=None):
        return '<a href="%s">%s</a>' % (self.test_result_admin_url(), text or str(self))

    @classmethod
    def test_results_for_object(cls, obj):
        model = obj._meta.model
        ct = ContentType.objects.get(app_label=model._meta.app_label, model=model._meta.model_name)
        TestMethod.add_test_methods_for_content_type(ct)
        missing_test_methods = TestMethod.objects.filter(content_type=ct).exclude(
            id__in=cls.objects.filter(content_type=ct,
                                      object_id=obj.pk).values_list(
                'test_method_id', flat=True))
        for test_method in missing_test_methods:
            cls.objects.create(content_type=ct, object_id=obj.pk, test_method=test_method)
        return cls.objects.filter(content_type=ct, object_id=obj.pk)

    @classmethod
    def rerun_tests_for_object(cls, obj):
        for test_result in cls.test_results_for_object(obj):
            test_result.run_test_method()
