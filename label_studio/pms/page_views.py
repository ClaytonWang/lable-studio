#!/usr/bin/env python
# encoding: utf-8

"""
  > FileName: serializer.py
  > Author: Yin
  > Mail: jindu.yin@digitalbrain.cn
  > CreatedTime: 2022/5/13 17:05
"""
import logging
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import PmsPage
from .services import generate_code
from .services import user_group_query
from .page_serializer import PmsPageCreatedSerializer
from .page_serializer import PmsPageDetailSerializer
from .page_serializer import PmsPageListSerializer
from .page_serializer import PmsPageUpdatedSerializer
from rest_framework.viewsets import ModelViewSet
from db_ml.common import MultiSerializerViewSetMixin
logger = logging.getLogger('info')


class PmsPageViews(MultiSerializerViewSetMixin, ModelViewSet):
    serializer_action_classes = {
        'list': PmsPageListSerializer,
        'retrieve': PmsPageDetailSerializer,
        'create': PmsPageCreatedSerializer,
        'update': PmsPageUpdatedSerializer,
        'partial_update': PmsPageUpdatedSerializer,
    }
    # permission_classes = [IsAdminOrSuperAdminCreatedUpdated]

    def list(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return: dict
        """
        data = request.GET.dict()
        name = data.get('name')
        search = data.get('search')
        self.queryset = PmsPage.objects.filter(is_delete=False)
        if name:
            self.queryset = self.queryset.filter(name=name)
        elif search:
            self.queryset = self.queryset.filter(
                Q(name__icontains=search) | Q(remark__icontains=search)
            )
        return super(PmsPageViews, self).list(request, *args, **kwargs)

    @action(detail=False)
    def user_page(self, request):
        """
        获取指定用户 菜单权限
        :param request:
        :return:
        """
        params = request.GET.dict()
        user_id = params.get('user')
        pms_type = params.get('pms_type', 'all')
        user = User.objects.filter(id=user_id).first()
        if not user:
            logger.warning(f'用户ID:{user_id}不存在。')
            return Response(status=400, data=dict(detail='用户不存在'))

        query = user_group_query(user, PmsPage, pms_type)
        query_vls = query.values('name', 'code', 'title', 'id').all()
        return Response(data=dict(results=list(query_vls)))

    @action(detail=False)
    def group_page(self, request):
        """
        获取指定分组 菜单权限
        :param request:
        :return:
        """
        params = request.GET.dict()
        group_id = params.get('group')
        group = Group.objects.filter(id=group_id).first()
        if not group:
            logger.warning(f'分组ID:{group_id}不存在。')
            return Response(status=400, data=dict(detail='用户组不存在'))

        query = PmsPage.objects.filter(is_delete=False, group=group)
        query_vls = query.values('name', 'code', 'title', 'id').all()
        return Response(data=dict(results=list(query_vls)))

    def retrieve(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.queryset = PmsPage.objects.filter(pk=kwargs.get('pk'))
        return super(PmsPageViews, self).retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data
        # 并发建菜单会有code冲突风险
        state, code = generate_code(
            data.get('parent_code'), data.get('project')
        )
        if not state:
            return Response(status=400, data=dict(detail=code))
        request.data['code'] = code
        return super(PmsPageViews, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.data.get('code'):
            return Response(status=400, data=dict(detail='菜单不能更新code'))
        self.queryset = PmsPage.objects.filter(pk=kwargs.get('pk'))
        return super(PmsPageViews, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.update(request, args, kwargs)

    def destroy(self, request, *args, **kwargs):
        self.queryset = PmsPage.objects.filter(pk=kwargs.get('pk'))
        instance = self.get_object()
        if instance.group.count() or instance.user.count():
            return Response(
                status=400, data=dict(detail=f'请先解除菜单:{instance.title}的权限')
            )
        super(PmsPageViews, self).destroy(request, *args, **kwargs)
        return Response(status=200, data=dict(msg='删除成功'))
