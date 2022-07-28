#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : api_set.py
  > CreateTime : 2022/7/25 14:56
"""
import logging
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from projects.models import ProjectSet
from projects.serializers_set import ProjectSetListSerializer
from projects.serializers_set import ProjectSetDetailSerializer
from projects.serializers_set import ProjectSetCreateSerializer
from projects.serializers_set import ProjectSetUpdateSerializer
from db_ml.common import DbPageNumberPagination
from db_ml.common import MultiSerializerViewSetMixin

logger = logging.getLogger(__name__)


class ProjectSetViews(MultiSerializerViewSetMixin, ModelViewSet):
    serializer_action_classes = {
        'list': ProjectSetListSerializer,
        'retrieve': ProjectSetDetailSerializer,
        'create': ProjectSetCreateSerializer,
        'update': ProjectSetUpdateSerializer,
        'partial_update': ProjectSetUpdateSerializer,
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
        self.queryset = ProjectSet.objects.for_user_organization(request.user)
        return super(ProjectSetViews, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.queryset = ProjectSet.objects.filter(pk=kwargs.get('pk'))
        return super(ProjectSetViews, self).retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.POST.dict()
        if not data:
            data = request.data
        title = data.get('title')
        if not title:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=dict(error='Invalid title')
            )

        data['created_by_id'] = request.user.id
        data['updated_by_id'] = request.user.id
        data['organization_id'] = request.user.active_organization.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        self.queryset = ProjectSet.objects.filter(pk=kwargs.get('pk'))
        return super(ProjectSetViews, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        data = request.POST.dict()
        if not data:
            data = request.data
        data['updated_by_id'] = request.user.id
        self.queryset = ProjectSet.objects.filter(pk=kwargs.get('pk'))
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        self.queryset = ProjectSet.objects.filter(pk=kwargs.get('pk'))
        if self.queryset:
            instance = self.queryset.first()
            count = instance.project_set.count()
            if count:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data=dict(error=f'项目集关联还{count}项目')
                )
        super(ProjectSetViews, self).destroy(request, *args, **kwargs)
        return Response(status=200, data=dict(message='删除成功'))

    @action(methods=['GET'], detail=False)
    def project(self, request, *args, **kwargs):
        query = ProjectSet.objects.for_user_organization(request.user).values('id', 'title')
        return Response(status=status.HTTP_201_CREATED, data=list(query))
