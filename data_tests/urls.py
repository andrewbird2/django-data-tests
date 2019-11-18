# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views


app_name = 'data_tests'
urlpatterns = [
    url(
        regex="^TestResult/~create/$",
        view=views.TestResultCreateView.as_view(),
        name='TestResult_create',
    ),
    url(
        regex="^TestResult/(?P<pk>\d+)/~delete/$",
        view=views.TestResultDeleteView.as_view(),
        name='TestResult_delete',
    ),
    url(
        regex="^TestResult/(?P<pk>\d+)/$",
        view=views.TestResultDetailView.as_view(),
        name='TestResult_detail',
    ),
    url(
        regex="^TestResult/(?P<pk>\d+)/~update/$",
        view=views.TestResultUpdateView.as_view(),
        name='TestResult_update',
    ),
    url(
        regex="^TestResult/$",
        view=views.TestResultListView.as_view(),
        name='TestResult_list',
    ),
	]
