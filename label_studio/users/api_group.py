#!/usr/bin/env python
# encoding: utf-8

"""
  > FileName   : group_views.py.py
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > CreateTime : 2021/6/18 09:26
"""
import logging
from django.contrib.auth.models import Group
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers_group import GroupListSerializer
from .serializers_group import GroupDetailSerializer
from .serializers_group import GroupCreatedSerializer
from .serializers_group import GroupUpdatedSerializer
# from base.models import PmsPage
# from base.models import PmsButton
# from .services import update_auth_page_or_btn
# from settings import SYSTEM_GROUP
from db_ml.common import MultiSerializerViewSetMixin

logger = logging.getLogger('info')


class GroupViews(MultiSerializerViewSetMixin, ModelViewSet):
    serializer_action_classes = {
        'list': GroupListSerializer,
        'retrieve': GroupDetailSerializer,
        'create': GroupCreatedSerializer,
        'update': GroupUpdatedSerializer,
        'partial_update': GroupUpdatedSerializer,
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
        self.queryset = Group.objects.all()
        if name:
            self.queryset = self.queryset.filter(name=name)
        elif search:
            self.queryset = self.queryset.filter(name__icontains=search)
        return super(GroupViews, self).list(request, *args, **kwargs)

    @action(detail=False)
    def get_group_page(self, request):
        """
        分组 菜单
        :param request:
        :return:
        """
        group_id = request.GET.dict().get('group')
        group = Group.objects.filter(id=group_id).first()
        if not group:
            return Response(status=400, data=dict(detail='需要指定分组'))
        query = group.pms_group.all()
        query_vls = query.values('name', 'code', 'title', 'id').all()
        return Response(data=dict(results=list(query_vls)))

    @action(detail=False)
    def get_group_btn(self, request):
        """
        分组 按键
        :param request:
        :return:
        """
        group_id = request.GET.dict().get('group')
        group = Group.objects.filter(id=group_id).first()
        if not group:
            return Response(status=400, data=dict(detail='需要指定分组'))
        query = group.pms_btn_group.all()
        query_vls = query.values(
            'name', 'code', 'page__code', 'page__name', 'page__title', 'id'
        ).all()
        return Response(data=dict(results=list(query_vls)))

    @action(methods=['PUT'], detail=False)
    def update_group_page(self, request):
        """
        更新分组 菜单权限
        :param request:
        :return:
        """
        page = request.data.get('page')
        if not request.data.get('group') or not isinstance(page, list):
            return Response(status=400, data=dict(detail='需要指定分组'))

        state, msg = update_auth_page_or_btn(request, PmsPage, 'page')
        logger.info(f'page add group: {msg}')
        # TODO 异常回滚
        # if not state or not _state:
        #     return Response(status=400, data=dict(detail=f'{msg}_{_msg}'))
        return Response(data=dict(results=msg))

    @action(methods=['PUT'], detail=False)
    def update_group_btn(self, request):
        if not request.data.get('group') or not request.data.get('btn'):
            return Response(status=400, data=dict(detail='需要指定分组和按键'))

        state, msg = update_auth_page_or_btn(request, PmsButton, 'btn')
        logger.info(f'group add btn: {msg}')
        # TODO 异常回滚
        return Response(data=dict(results=msg))

    def retrieve(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.queryset = Group.objects.filter(pk=kwargs.get('pk'))
        return super(GroupViews, self).retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data
        name = data.get('name')
        if not name:
            return Response(status=400, data=dict(detail='缺少分组名'))
        obj, is_create = Group.objects.get_or_create(
            name=name, defaults=dict(name=name)
        )
        if not is_create:
            return Response(status=400, data=dict(detail=f'{name}分组存在'))
        return Response(status=201, data=dict(name=name, id=obj.id))

    def update(self, request, *args, **kwargs):
        self.queryset = Group.objects.filter(pk=kwargs.get('pk'))
        for item in self.queryset:
            if item.name in SYSTEM_GROUP:
                return Response(
                    status=400,
                    data=dict(detail=f'用户{item.name}不能更新。')
                )
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        self.update(request, args, kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        删除分组 admin superadmin guest showpwd 不能删除
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.queryset = Group.objects.filter(pk=kwargs.get('pk'))
        instance = self.get_object()
        if instance.name in SYSTEM_GROUP:
            return Response(
                status=400,
                data=dict(detail=f'用户{instance.name}不能删除。')
            )

        if instance.pms_group.count() or instance.pms_btn_group.count():
            return Response(
                status=400, data=dict(detail=f'请先解除分组{instance.name}的权限')
            )
        instance.delete()
        return Response(status=200, data=dict(msg='删除成功'))

        '''
        # 删除分组，主动删除关联的用户、菜单、按键
        # 1.删除分组关联的用户
        # 2.删除分组下的菜单
        # 3.删除分组的按键
        data = request.data
        pk = kwargs.pop('pk')
        group_name = data.get('name')
        if group_name in SYSTEM_GROUP:
            return Response(
                status=400,
                data=dict(detail=f'用户{group_name}不能删除。')
            )

        group = Group.objects.get(pk=pk)
        # 删除关联组关联用户
        u_query = User.objects.filter(groups=group)
        for item in u_query:
            item.groups.remove(group)
        # 删除组关联的菜单
        m_query = PmsPage.objects.filter(group=group)
        for item in m_query:
            item.group.remove(group)
        # 删除组关联的按键
        b_query = PmsButton.objects.filter(group=group)
        for item in b_query:
            item.group.remove(group)

        group.delete()
        return Response(status=204, data=dict(msg='删除成功'))
        '''

    @action(methods=['GET'], detail=False)
    def all(self, request, *args, **kwargs):
        queryset = Group.objects.values('id', 'name')
        return Response(data=list(queryset))
