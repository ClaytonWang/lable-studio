#!/usr/bin/env python
# encoding: utf-8

"""
  > FileName: serializer.py
  > Author: Yin
  > Mail: jindu.yin@digitalbrain.cn
  > CreatedTime: 2022/10/17 17:05
"""
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PmsPage
from .models import PmsButton
from .services import user_group_query
from .services import generate_btn_code
from .button_serializer import PmsBtnListSerializer
from .button_serializer import PmsBtnDetailSerializer
from .button_serializer import PmsBtnCreatedSerializer
from .button_serializer import PmsBtnUpdatedSerializer
from rest_framework.viewsets import ModelViewSet
from db_ml.common import MultiSerializerViewSetMixin
import logging
logger = logging.getLogger('info')


class PmsBtnViews(MultiSerializerViewSetMixin, ModelViewSet):
    serializer_action_classes = {
        'list': PmsBtnListSerializer,
        'retrieve': PmsBtnDetailSerializer,
        'create': PmsBtnCreatedSerializer,
        'update': PmsBtnUpdatedSerializer,
        'partial_update': PmsBtnUpdatedSerializer,
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
        page_code = data.get('page_code')
        self.queryset = PmsButton.objects.filter(is_delete=False)
        if search:
            self.queryset = self.queryset.filter(
                Q(name__icontains=search) | Q(remark__icontains=search)
            )
        if page_code:
            self.queryset = self.queryset.filter(page__code=page_code)
        if name:
            self.queryset = self.queryset.filter(name=name)

        return super(PmsBtnViews, self).list(request, *args, **kwargs)

    @action(detail=False)
    def user_btn(self, request):
        """
        获取指定用户 按键
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

        query = user_group_query(user, PmsButton, pms_type)
        query_vls = query.values(
            'name', 'code', 'page__code', 'page__name', 'page__title', 'id'
        ).all()
        return Response(data=dict(results=list(query_vls)))

    @action(detail=False)
    def group_btn(self, request):
        """
        获取指定分组 按键权限
        :param request:
        :return:
        """
        params = request.GET.dict()
        group_id = params.get('group')
        group = Group.objects.filter(id=group_id).first()
        if not group:
            logger.warning(f'分组ID:{group_id}不存在。')
            return Response(status=400, data=dict(detail='用户组不存在'))

        query = PmsButton.objects.filter(is_delete=False, group=group)
        query_vls = query.values(
            'name', 'code', 'page__code', 'page__name', 'page__title', 'id'
        ).all()
        return Response(data=dict(results=list(query_vls)))

    def retrieve(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.queryset = PmsButton.objects.filter(pk=kwargs.get('pk'))
        return super(PmsBtnViews, self).retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data
        page_code = data.get('page_code')
        page = PmsPage.objects.filter(code=page_code).first()
        if not page:
            return Response(
                status=400, data=dict(detail="Not query page code")
            )
        code = generate_btn_code(page)
        request.data['code'] = code
        request.data['page'] = page.id
        return super(PmsBtnViews, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.data.get('code'):
            return Response(status=400, data=dict(detail='按键不能更新code'))

        self.queryset = PmsButton.objects.filter(pk=kwargs.get('pk'))
        rst = super(PmsBtnViews, self).update(request, *args, **kwargs)
        rst.data.pop('page')
        return rst

    def partial_update(self, request, *args, **kwargs):
        self.update(request, args, kwargs)

    def destroy(self, request, *args, **kwargs):
        self.queryset = PmsButton.objects.filter(pk=kwargs.get('pk'))
        instance = self.get_object()
        if instance.group.count() or instance.user.count():
            return Response(
                status=400, data=dict(detail=f'请先解除按键:{instance.name}的权限')
            )
        super(PmsBtnViews, self).destroy(request, *args, **kwargs)
        return Response(status=200, data=dict(results='删除成功'))
