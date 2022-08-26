#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : api_train.py
  > CreateTime : 2022/8/2 16:32
"""
import os
import math
import json
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
from tasks.models import Task, Annotation, Prediction
from db_ml.common import DbPageNumberPagination
from db_ml.common import MultiSerializerViewSetMixin
from db_ml.services import get_choice_values

logger = logging.getLogger(__name__)


class ModelTrainViews(MultiSerializerViewSetMixin, ModelViewSet):
    serializer_action_classes = {
        'list': ModelTrainListSerializer,
        'retrieve': ModelTrainDetailSerializer,
        'create': ModelTrainCreateSerializer,
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
        filter_keys = ['project_id', 'model_id', 'user_id', 'project_set_id']
        data = request.GET.dict()
        filter_params = dict()
        for key in filter_keys:
            value = data.get(key)
            if not value:
                continue
            if key == 'user_id':
                filter_params['created_by_id'] = value
            elif key == 'project_set_id':
                filter_params['project__set_id'] = value
            elif key == 'is_train':
                if value == 'true':
                    filter_params['is_train'] = True
                elif value == 'false':
                    filter_params['is_train'] = False
            else:
                filter_params[key] = value
        if not filter_params.get('project_id'):
            raise Exception('必须指定项目')
        self.queryset = ModelTrain.objects.filter(**filter_params).order_by('-created_at')
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

        return Response(status=status.HTTP_200_OK, data=result)

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

    @action(methods=['GET'], detail=False)
    def config(self, request, *args, **kwargs):
        with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
            data = json.loads(f.read())
            return Response(data=data)

    @action(methods=['GET'], detail=False)
    def init(self, request, *args, **kwargs):
        """
        新增评估&新增训练的初始数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        params = request.GET.dict()
        model_id = params.get('model_id')
        project_id = params.get('project_id')
        operate = params.get('operate', 'assessment')

        project = Project.objects.filter(id=project_id).first()
        if project.template_type != 'intent-dialog':
            raise Exception('项目模版类型错误，支持模版是对话意图识别。')

        tasks = Task.objects.filter(project_id=project_id)
        anno_query = Annotation.objects.filter(task__in=tasks)
        anno_result = {str(item.task_id): item.result for item in anno_query}
        pre_query = Prediction.objects.filter(task__in=tasks)
        pre_result = {str(item.task_id): item.result for item in pre_query}

        # TODO 手动标注和自动标注，历史数据引起的错误
        exactness_count, error_count, total_count, accuracy_rate = 0, 0, 0, 0
        for task_id, result in pre_result.items():
            if task_id not in anno_result:
                exactness_count += 1
                continue

            pre_labels = get_choice_values(result)
            ann_labels = get_choice_values(anno_result[task_id])
            if ann_labels == pre_labels:
                exactness_count += 1
                continue

            error_count += 1

        task_count = tasks.count()
        result = dict(
            model_id=model_id,
            project_id=project_id,
            project_title=project.title,
            total_count=task_count,
            exactness_count=exactness_count,
            accuracy_rate=round(exactness_count/task_count, 2),
        )

        if operate == 'train':
            train_task = math.floor(task_count * 0.8)
            if model_id:
                model = ModelManager.objects.filter(id=model_id).first()
                max_version_model = ModelManager.objects.filter(token=model.token).order_by('-version').first()
                result['version'] = model.version
                result['new_version'] = str(format(float(max_version_model.version) + 1, '.1f'))
            else:
                result['version'] = '0.0'
                result['new_version'] = '1.0'
            result['new_model_train_task'] = train_task
            result['new_model_assessment_task'] = task_count - train_task

        return Response(data=result)

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
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        return Response(data)

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
        data = self.get_train_assessment_params(request)
        serializer = ModelTrainCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @staticmethod
    def get_train_assessment_params(request):
        data = request.POST.dict()
        if not data:
            data = request.data

        data['category'] = 'assessment'
        data['created_by_id'] = request.user.id
        data['updated_by_id'] = request.user.id
        data['organization_id'] = request.user.active_organization.id
        return data

    def destroy(self, request, *args, **kwargs):
        self.queryset = ModelTrain.objects.filter(pk=kwargs.get('pk'))
        if len(self.queryset) and self.queryset[0].category != 'assessment':
            raise Exception('只能删除评估模型')
        super(ModelTrainViews, self).destroy(request, *args, **kwargs)
        return Response(status=200, data=dict(message='删除成功'))
