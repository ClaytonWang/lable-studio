#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : common.py
  > CreateTime : 2022/7/25 16:13
"""
from rest_framework.pagination import PageNumberPagination
from django.db.models import Manager


class DbPageNumberPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'


class DbOrganizationManager(Manager):
    def for_user_organization(self, user):
        return self.filter(organization=user.active_organization)


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
                raise ValueError('{} serializer is not defined'.format(
                    self.action)
                )
            else:
                return default_class_item
        return class_item
