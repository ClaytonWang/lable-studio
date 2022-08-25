#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : api_train.py
  > CreateTime : 2022/8/2 16:32
"""
import logging
import pathlib
from urllib import parse
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from django.db.models import F, Q
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from model_manager.serializers_train import ModelTrainListSerializer
from model_manager.serializers_train import ModelTrainDetailSerializer
from model_manager.serializers_train import ModelTrainCreateSerializer
from model_manager.serializers_train import ModelTrainUpdateSerializer
from model_manager.models import ModelTrain, ModelManager
from projects.models import ProjectSet, Project
from db_ml.common import DbPageNumberPagination
from db_ml.common import MultiSerializerViewSetMixin

logger = logging.getLogger(__name__)


class ModelTrainViews(MultiSerializerViewSetMixin, ModelViewSet):
    serializer_action_classes = {
        'list': ModelTrainListSerializer,
        'retrieve': ModelTrainDetailSerializer,
        # 'create': ModelTrainCreateSerializer,
        # 'update': ModelTrainUpdateSerializer,
        # 'partial_update': ModelTrainUpdateSerializer,
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
        project_id = data.get('project_id')
        if not project_id:
            raise Exception('必须指定项目')

        self.queryset = ModelTrain.objects.filter(
            project_id=project_id
        ).order_by('-created_at')
        return super(ModelTrainViews, self).list(request, *args, **kwargs)

    @action(methods=['GET'], detail=False)
    def select(self, request, *args, **kwargs):
        project_id = request.GET.dict().get('project_id')
        model_query = self.get_model_of_project(project_id)
        models = model_query.distinct('title', 'version')
        users = ModelTrain.objects.annotate(
            user_id=F('created_by__id'), username=F('created_by__username')
        ).filter(project_id=project_id)\
            .values('user_id', 'username').distinct('username')
        project_set = ProjectSet.objects.filter(project_set__id=project_id).values(
            'id', 'title'
        ).distinct()

        result = dict(
            models=list(models),
            users=list(users),
            train=[{True: '是'}, {False: '否'}],
            project_sets=list(project_set),
        )

        return Response(status=status.HTTP_201_CREATED, data=result)

    @action(methods=['GET'], detail=False)
    def model(self, request, *args, **kwargs):
        """
        选取 对话意图分类 对话生成 的模型
        模型的选择，选择模型的project_id是null的model或是project_id等于当前项目的project_id
        :return:
        """
        project_id = request.GET.dict().get('project_id')
        data = self.get_model_of_project(project_id)
        return Response(data=list(data))

    @staticmethod
    def get_model_of_project(project_id):
        queryset = ModelManager.objects.filter(
            Q(type__in=('intention', 'generation'), project_id__isnull=True) |
            Q(project_id__id=project_id)
        ).values('id', 'title', 'version')
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.queryset = ModelTrain.objects.filter(pk=kwargs.get('pk'))
        return super(ModelTrainViews, self).retrieve(request, *args, **kwargs)

    @action(methods=['POST'], detail=False)
    def train(self, request, *args, **kwargs):
        """
        新增训练接口
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        pass

    @action(methods=['POST'], detail=False)
    def assessment(self, request, *args, **kwargs):
        """
        新增评估接口
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def destroy(self, request, *args, **kwargs):
        self.queryset = ModelTrain.objects.filter(pk=kwargs.get('pk'))
        if len(self.queryset) and self.queryset[0].category != 'assessment':
            raise Exception('只能删除评估模型')
        super(ModelTrainViews, self).destroy(request, *args, **kwargs)
        return Response(status=200, data=dict(message='删除成功'))
