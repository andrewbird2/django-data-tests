# -*- coding: utf-8 -*-
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import (
	TestResult,
)


class TestResultCreateView(CreateView):

    model = TestResult


class TestResultDeleteView(DeleteView):

    model = TestResult


class TestResultDetailView(DetailView):

    model = TestResult


class TestResultUpdateView(UpdateView):

    model = TestResult


class TestResultListView(ListView):

    model = TestResult

