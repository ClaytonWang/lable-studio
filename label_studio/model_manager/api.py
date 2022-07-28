"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
import pathlib
from urllib import parse
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from model_manager.serializers import ModelManagerListSerializer
from model_manager.serializers import ModelManagerDetailSerializer
from model_manager.serializers import ModelManagerCreateSerializer
from model_manager.serializers import ModelManagerUpdateSerializer
from model_manager.models import ModelManager
from model_manager.models import MODEL_TYPE
from model_manager.services import ml_backend_request
from db_ml.common import DbPageNumberPagination
from db_ml.common import MultiSerializerViewSetMixin

logger = logging.getLogger(__name__)


class ModelManagerViews(MultiSerializerViewSetMixin, ModelViewSet):
    serializer_action_classes = {
        'list': ModelManagerListSerializer,
        'retrieve': ModelManagerDetailSerializer,
        'create': ModelManagerCreateSerializer,
        'update': ModelManagerUpdateSerializer,
        'partial_update': ModelManagerUpdateSerializer,
    }
    pagination_class = DbPageNumberPagination

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
        self.queryset = ModelManager.objects.\
            for_user_organization(request.user).order_by('-created_at')
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
        self.queryset = ModelManager.objects.filter(pk=kwargs.get('pk'))
        return super(ModelManagerViews, self).partial_update(
            request, *args,**kwargs)

    def destroy(self, request, *args, **kwargs):
        self.queryset = ModelManager.objects.filter(pk=kwargs.get('pk'))
        super(ModelManagerViews, self).destroy(request, *args, **kwargs)
        return Response(status=200, data=dict(message='删除成功'))

    @action(methods=['GET'], detail=False)
    def select(self, request, *args, **kwargs):
        query = ModelManager.objects.values('version').distinct()
        result = dict(
            type=dict(MODEL_TYPE),
            version=[item['version'] for item in query],
            model_set=[],
            project_set=[],
        )

        return Response(status=status.HTTP_201_CREATED, data=result)

    @action(methods=['GET'], detail=False)
    def export(self, request, *args, **kwargs):
        url = request.GET.dict('url')
        if not url:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=dict(error="Invalid URL")
            )
        state, rsp = ml_backend_request(
            opt='export', method='get', params=dict(url=url)
        )
        if state:
            return Response(data=rsp)
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=dict(error='ML Backend request error.')
            )

