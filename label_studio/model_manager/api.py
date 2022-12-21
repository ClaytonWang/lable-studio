"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
import pathlib
import distutils
from urllib import parse
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from django.db.models import Q
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
from model_manager.models import MODEL_TYPE, TEMPLATE_MODEL_TYPE_MAPPING
from model_manager.services import ml_backend_request
from db_ml.common import DbPageNumberPagination
from db_ml.common import MultiSerializerViewSetMixin
from projects.models import ProjectSet

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
        模型列表过滤，同时查询多个模型类型，模型类型之间用【半角逗号】隔开
        :param request:
        :param args:
        :param kwargs:
        :return: dict
        """
        data = request.GET.dict()
        _type = data.get('type')
        template_type = data.get('template_type')
        version = data.get('version')
        model = data.get('model_set')
        project = data.get('project_set')
        self.queryset = ModelManager.objects.\
            for_user_organization(request.user).order_by('-created_at')
        template_type = dict(TEMPLATE_MODEL_TYPE_MAPPING).get(template_type)
        filter_params = dict(is_delete=False)
        base = data.get('base')
        if base:
            filter_params['base'] = distutils.util.strtobool(base)
        if _type:
            _type = _type.split(',')
            filter_params['type__in'] = _type
        if version:
            filter_params['version'] = version
        if model:
            filter_params['title'] = model
        if template_type:
            filter_params['type'] = template_type
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
        url = data.get('url', '')
        params = parse.parse_qs(parse.urlparse(url).query)
        version = params.get('version', [])
        data['version'] = version[0] if len(version) else '1.0'
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
        """
        删除接口
        """
        self.queryset = ModelManager.objects.filter(pk=kwargs.get('pk'), base=False)
        if not self.queryset:
            return Response(status=400, data=dict(message='未查询到非基础模型'))
        else:
            self.queryset.update(is_delete=True)
            return Response(status=200, data=dict(message='删除成功'))

    @action(methods=['GET'], detail=False)
    def select(self, request, *args, **kwargs):
        query = ModelManager.objects.values('version').distinct()
        model_set_query = ModelManager.objects.values('title').distinct()
        project_set_query = ProjectSet.objects.values('title').distinct()

        result = dict(
            type=dict(MODEL_TYPE),
            version=[item['version'] for item in query],
            model_set=[item['title'] for item in model_set_query],
            project_set=[item['title'] for item in project_set_query],
        )

        return Response(status=status.HTTP_201_CREATED, data=result)

    @action(methods=['GET'], detail=True)
    def export(self, request, *args, **kwargs):
        # model = self.get_model(request)
        # url = request.GET.dict('url')
        query = ModelManager.objects.filter(pk=kwargs.get('pk')).first()
        url = query.url
        if not url:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=dict(error="Invalid ID")
            )
        # 测试
        # return Response(data={"download": url})
        # 调用算法服务
        state, rsp = ml_backend_request(
            ['export'], method='get',
            params=dict(hash_id=query.hash_id)
        )
        rsp_data = {"download": rsp}
        return self.return_ml_response(state, rsp_data)

    @action(methods=['GET'], detail=False)
    def label(self, request, *args, **kwargs):
        return Response(data=['a','b'])
        model = self.get_model(request)
        if not model:
            raise Exception('未查询到模型')

        state, rsp = ml_backend_request(
            uri=['getLabels'], method='get',
            params=dict(hasd_id=model.hash_id)
        )
        if state:
            return Response(data=rsp.values())
        return self.return_ml_response(state, rsp)

    @action(methods=['GET'], detail=False)
    def model(self, request, *args, **kwargs):
        queryset = ModelManager.objects.filter(
            type=request.GET.dict().get('type')).values(
            'id', 'title', 'version'
        )
        return Response(data=list(queryset))

    @staticmethod
    def get_model(request):
        model_id = request.GET.dict().get('model_id')
        model = ModelManager.objects.filter(id=model_id).first()
        return model

    @staticmethod
    def return_ml_response(state, rsp):
        if state:
            return Response(data=rsp)
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=dict(error=f'算法模块请求异常: {rsp}')
            )
