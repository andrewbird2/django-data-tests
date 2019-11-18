=====
Usage
=====

To use Django Data Tests in a project, add it to your `INSTALLED_APPS`:

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
