"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import data_export.api
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.conf.urls import url


# 增加promt - api.py
from . import api, views

app_name = 'model_configer'

# reverse for projects:name
_urlpatterns = [
    path('', views.model_list, name='models-index')
]

# reverse for projects:api:name
_api_urlpatterns = [

]

_api_urlpatterns_templates = [
]


urlpatterns = [
    path('model-configer/', include(_urlpatterns)),

]
