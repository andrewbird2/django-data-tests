=============================
Django Data Tests
=============================

.. image:: https://badge.fury.io/py/django-data-tests.svg
    :target: https://badge.fury.io/py/django-data-tests

.. image:: https://travis-ci.org/andrewbird2/django-data-tests.svg?branch=master
    :target: https://travis-ci.org/andrewbird2/django-data-tests

.. image:: https://codecov.io/gh/andrewbird2/django-data-tests/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/andrewbird2/django-data-tests

A Django app for specifying validation tests on data in your database.



Quickstart
----------

Install Django Data Tests::

    pip install django-data-tests

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'data_tests.apps.DataTestsConfig',
        ...
    )

Add a data test to one of your existing models

.. code-block:: python

    from data_tests.registry import test_method
    from django.db import models

    class Cat(models.Model):
        ...

        def make_noise(self):
            return 'Miaow!'

        @test_method('Check the cat miaows appropriately')
        def check_cat_sound(self):
            noise = self.noise()
            if noise != 'Miaow!':
                return False, 'Cat made the wrong noise: %s' % noise
            else:
                return True

You can run your data tests with the management command

.. code-block:: bash

    ./manage.py rundatatests

Alternatively, run them whenever the object is saved in the admin

.. code-block:: python

    from django.contrib import admin
    from data_tests.admin import DataTestsAdminMixin

    class CatAdmin(DataTestsAdminMixin, admin.ModelAdmin):
        ...


