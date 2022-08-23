#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : api_record.py
  > CreateTime : 2022/8/2 16:32
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
from model_manager.serializers_record import ModelRecordListSerializer
from model_manager.serializers_record import ModelRecordDetailSerializer
from model_manager.serializers_record import ModelRecordCreateSerializer
from model_manager.serializers_record import ModelRecordUpdateSerializer
from model_manager.models import ModelRecord
from db_ml.common import DbPageNumberPagination
from db_ml.common import MultiSerializerViewSetMixin

logger = logging.getLogger(__name__)


class ModelRecordViews(MultiSerializerViewSetMixin, ModelViewSet):
    serializer_action_classes = {
        'list': ModelRecordListSerializer,
        'retrieve': ModelRecordDetailSerializer,
        # 'create': ModelRecordCreateSerializer,
        # 'update': ModelRecordUpdateSerializer,
        # 'partial_update': ModelRecordUpdateSerializer,
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
        model_id = data.get('model_id')
        self.queryset = ModelRecord.objects.filter().order_by('-created_at')
        return super(ModelRecordViews, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.queryset = ModelRecord.objects.filter(pk=kwargs.get('pk'))
        return super(ModelRecordViews, self).retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.queryset = ModelRecord.objects.filter(pk=kwargs.get('pk'))
        if len(self.queryset) and self.queryset[0].category != 'assessment':
            raise Exception('只能删除评估模型')
        super(ModelRecordViews, self).destroy(request, *args, **kwargs)
        return Response(status=200, data=dict(message='删除成功'))
