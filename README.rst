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

Documentation
-------------

The full documentation is at https://django-data-tests.readthedocs.io.

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

Add Django Data Tests's URL patterns:

.. code-block:: python

    from data_tests import urls as data_tests_urls


    urlpatterns = [
        ...
        url(r'^', include(data_tests_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
