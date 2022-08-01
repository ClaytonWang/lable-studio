#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : api_sign.py
  > CreateTime : 2022/7/29 15:11
"""
import logging
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group
from users.models import SignUpInvite
from organizations.models import Organization
from users.serializers_sign import SignUpInviteListSerializer
from users.serializers_sign import SignUpInviteDetailSerializer
from users.serializers_sign import SignUpInviteCreateSerializer
from users.serializers_sign import SignUpInviteUpdateSerializer
from db_ml.common import DbPageNumberPagination
from db_ml.common import MultiSerializerViewSetMixin

logger = logging.getLogger(__name__)


class SignUpInviteViews(MultiSerializerViewSetMixin, ModelViewSet):
    serializer_action_classes = {
        'list': SignUpInviteListSerializer,
        'retrieve': SignUpInviteDetailSerializer,
        'create': SignUpInviteCreateSerializer,
        'update': SignUpInviteUpdateSerializer,
        'partial_update': SignUpInviteUpdateSerializer,
    }
    pagination_class = DbPageNumberPagination

    def get_queryset(self):
        return SignUpInvite.objects.all()

    def list(self, request, *args, **kwargs):
        return super(SignUpInviteViews, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.POST.dict()
        if not data:
            data = request.data

        data['created_by'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        check_rst = self.check_exists_code(serializer.code)
        if check_rst:
            return check_rst

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        self.queryset = SignUpInvite.objects.filter(pk=kwargs.get('pk'))
        return super(SignUpInviteViews, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.queryset = SignUpInvite.objects.filter(pk=kwargs.get('pk'))
        code = request.POST.dict().get('code')
        check_rst = self.check_exists_code(code)
        if check_rst:
            return check_rst

        return super(SignUpInviteViews, self).partial_update(
            request, *args, **kwargs
        )

    @staticmethod
    def check_exists_code(code):
        if SignUpInvite.objects.filter(code=code).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=dict(error=f'{code} 已经存在')
            )
        return None

    @action(methods=['GET'], detail=False)
    def select(self, request, *args, **kwargs):
        queryset_org = Organization.objects.values('id', 'title')
        queryset_group = Group.objects.values('id', 'name')
        result = dict(
            group=list(queryset_group),
            organization=list(queryset_org),
        )
        return Response(data=result)
