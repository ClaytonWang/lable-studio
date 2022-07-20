"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import data_export.api
from django.shortcuts import redirect
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from django.conf.urls import url


# 增加promt - api.py
from . import api, views
from .api import ModelConfigerViews

app_name = 'model_configer'

# reverse for projects:name
_urlpatterns = [
    path('', views.model_list, name='models-index')
]

# reverse for projects:api:name
router = DefaultRouter(trailing_slash=False)
router.register(r'', ModelConfigerViews, basename='model configer')
_api_urlpatterns = [
    path('', include(router.urls)),
]

_api_urlpatterns_templates = [
]


urlpatterns = [
    path('model-configer/', include(_urlpatterns)),
    path('api/model-configer', include(_api_urlpatterns)),

]
