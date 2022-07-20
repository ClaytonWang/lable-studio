"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import drf_yasg.openapi as openapi
import logging
import numpy as np
import pathlib
from urllib import parse

from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound, ValidationError as RestValidationError
from django.http import Http404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import status, filters
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet

from core.utils.common import temporary_disconnect_all_signals
from core.label_config import config_essential_data_has_changed
from projects.models import (Project, ProjectSummary, ProjectManager)
from projects.serializers import (ProjectSerializer, ProjectLabelConfigSerializer, ProjectSummarySerializer)
from projects.functions.next_task import get_next_task
from tasks.models import Task
from webhooks.utils import emit_webhooks_for_instance
from webhooks.utils import api_webhook, api_webhook_for_delete
from webhooks.models import WebhookAction

from data_manager.models import View
from core.permissions import all_permissions, ViewClassPermission
from model_manager.serializers import ModelManagerListSerializer
from model_manager.serializers import ModelManagerDetailSerializer
from model_manager.serializers import ModelManagerCreateSerializer
from model_manager.serializers import ModelManagerUpdateSerializer
from model_manager.models import ModelManager

logger = logging.getLogger(__name__)


class ProjectListPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'


class MultiSerializerViewSetMixin(object):
    def get_serializer_class(self):
        assert type(self.serializer_action_classes) is dict

        default_action = 'retrieve'
        actions = self.serializer_action_classes.keys()
        if not actions:
            raise ValueError('serializer_action_classes is not defined.')
        if default_action not in actions:
            default_action = list(actions)[0]

        default_class_item = self.serializer_action_classes.get(default_action)
        class_item = self.serializer_action_classes.get(self.action)
        if not class_item:
            if not default_class_item:
                raise ValueError('{} serializer is not defined'.format(self.action))
            else:
                return default_class_item
        return class_item


class ModelManagerViews(MultiSerializerViewSetMixin, ModelViewSet):
    serializer_action_classes = {
        'list': ModelManagerListSerializer,
        'retrieve': ModelManagerDetailSerializer,
        'create': ModelManagerCreateSerializer,
        'update': ModelManagerUpdateSerializer,
        'partial_update': ModelManagerUpdateSerializer,
    }
    pagination_class = ProjectListPagination

    def list(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return: dict
        """
        data = request.GET.dict()
        _type = data.get('type')
        version = data.get('version')
        model = data.get('model')
        project = data.get('project')
        self.queryset = ModelManager.objects.for_user_organization(request.user)
        filter_params = dict()
        if _type:
            filter_params['type'] = _type
        if version:
            filter_params['version'] = version
        if model:
            filter_params['model'] = model
        if project:
            filter_params['project'] = project
        if filter_params:
            self.queryset = self.queryset.filter(**filter_params)
        return super(ModelManagerViews, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.queryset = ModelManager.objects.filter(pk=kwargs.get('pk'))
        return super(ModelManagerViews, self).retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.POST.dict()
        if not data:
            data = request.data
        params = parse.parse_qs(parse.urlparse(data.get('url', '')).query)
        version = params.get('version', [])
        data['version'] = version[0] if len(version) else ''
        data['created_by_id'] = request.user.id
        data['organization_id'] = request.user.active_organization.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def update(self, request, *args, **kwargs):
        self.queryset = ModelManager.objects.filter(pk=kwargs.get('pk'))
        return super(ModelManagerViews, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, args, kwargs)

    def destroy(self, request, *args, **kwargs):
        self.queryset = ModelManager.objects.filter(pk=kwargs.get('pk'))
        super(ModelManagerViews, self).destroy(request, *args, **kwargs)
        return Response(status=200, data=dict(msg='删除成功'))
