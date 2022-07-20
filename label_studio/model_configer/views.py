"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import json
import logging
import lxml.etree
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.exceptions import ValidationError


logger = logging.getLogger(__name__)


@login_required
def model_list(request):
    return render(request, 'model_configer/list.html')


