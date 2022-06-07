#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : api_db.py
  > CreateTime : 2022/6/7 10:12
"""

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from tasks.tag_serializers import TagListSerializer
from tasks.tag_serializers import TagDetailSerializer
from tasks.tag_serializers import TagCreatedSerializer
from tasks.tag_serializers import TagUpdatedSerializer
from tasks.models import TaskDbTag


class DbTaskTagViews(ModelViewSet):
    serializer_action_classes = {
        'list': TagListSerializer,
        'retrieve': TagDetailSerializer,
        'create': TagCreatedSerializer,
        'update': TagUpdatedSerializer,
        'partial_update': TagUpdatedSerializer,
    }

    def get_serializer_class(self):
        """
        """
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

    def list(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return: dict
        """

        self.queryset = TaskDbTag.objects.all()
        return super(DbTaskTagViews, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.queryset = TaskDbTag.objects.filter(pk=kwargs.get('pk'))
        return super(DbTaskTagViews, self).retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super(DbTaskTagViews, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.queryset = TaskDbTag.objects.filter(pk=kwargs.get('pk'))
        return super(DbTaskTagViews, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.update(request, args, kwargs)

    def destroy(self, request, *args, **kwargs):
        self.queryset = TaskDbTag.objects.filter(pk=kwargs.get('pk'))
        super(DbTaskTagViews, self).destroy(request, *args, **kwargs)
        return Response(status=200, data=dict(msg='Is Ok'))
