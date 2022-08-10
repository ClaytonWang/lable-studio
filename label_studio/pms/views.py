#!/usr/bin/env python
# encoding: utf-8

"""
  > FileName: views.py
  > Author: Yin
  > Mail: jindu.yin@digitalbrain.cn
  > CreatedTime: 2022/04/17 17:05
"""
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import PmsPage
from .models import PmsButton
from .services import join_menu
from .services import get_user_btn
from .services import user_group_query
from users.serializers import UserSimpleSerializer
from .services import generate_code
from .services import user_access


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def menu_tree(request):
    """
    权限设置页面提供所有菜单&按键，包括是否有权限
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    params = request.GET.dict()
    user_id, group_id = None, None
    merge = params.get('merge')
    if isinstance(merge, str):
        merge = True if merge.lower() == 'true' else False
    if params.get('choice') == 'account':
        user_id = params.get('select_id')
    else:
        group_id = params.get('select_id')

    # 查询所有菜单页
    menu_queryset = PmsPage.objects.filter(is_delete=False).values(
        'name', 'code', 'id', 'title'
    ).order_by('code').all()
    menus = [
        dict(dict(expand=False, checked=False), **dict(item))
        for item in menu_queryset
    ]

    # 查询所有按键
    btn_query = PmsButton.objects.filter(is_delete=False).values(
        'name', 'code', 'page', 'id'
    )
    btns = [dict(dict(checked=False), **dict(item)) for item in btn_query]

    # 菜单 & 按键 添加权限
    choice_menu = None
    choice_btn = None

    # 选中账号，账号已有的权限
    # 选中账号会把分组内的权限做并集处理
    if user_id:
        user_id = int(user_id)
        user = User.objects.get(pk=user_id)
        if merge: # 合并账号和分组权限
            choice_menu = user_group_query(user=user, pms_model=PmsPage)
            choice_btn = user_group_query(user=user, pms_model=PmsButton)
        else:
            choice_menu = PmsPage.objects.filter(is_delete=False, user=user)
            choice_btn = PmsButton.objects.filter(is_delete=False, user=user)

    # 选中分组，分组已有的权限
    if group_id:
        group_id = int(group_id)
        group = Group.objects.get(pk=group_id)
        choice_menu = PmsPage.objects.filter(is_delete=False, group=group)
        choice_btn = PmsButton.objects.filter(is_delete=False, group=group)

    if choice_menu:
        for item in choice_menu:
            for index, menu in enumerate(menus):
                if menu.get('code') == item.code:
                    menus[index] = dict(
                        menus[index], **dict(expand=True, checked=True)
                    )
    if choice_btn:
        for item in choice_btn:
            for index, btn in enumerate(btns):
                if btn.get('code') == item.code:
                    btns[index] = dict(
                        btns[index], **dict(checked=True)
                    )

    # 按键根据页面归类
    btn_res = dict()
    for item in btns:
        page_id = str(item['page'])
        if page_id in btn_res:
            tmp = btn_res[page_id]
            tmp.append(item)
            btn_res[page_id] = tmp
        else:
            btn_res[page_id] = [item]

    # 按键放到页面
    for page_no, t_btn in btn_res.items():
        for index, item in enumerate(menus):
            if str(item['id']) == page_no:
                menus[index]['buttons'] = t_btn

    # 菜单父子结构
    new_menus = sorted(menus, key=lambda item: int(item['code']))
    results = []
    for _menu in new_menus:
        results = join_menu(_menu, results, level=0)

    def update_expand(tmp):
        children = tmp.get('children')
        for item in children:
            if item.get('checked'):
                return True
        return False
    for index, item in enumerate(menus):
        state = update_expand(item)
        if state:
            menus[index]['expand'] = True

    return Response(data=dict(results=results))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    """
    :param request:
    :return:
    """
    # params = request.GET.dict()
    # token = params.get('token', None)
    # obj = Token.objects.filter(key=token).first()
    #
    # if not obj:
    #     return Response(status=400, data=dict(detail='Invalid Token'))

    user = request.user
    results = UserSimpleSerializer(instance=user).data
    query_pms = user_group_query(user, PmsPage)
    pms = query_pms.values('name', 'title', 'code')
    acs = user_access(user)
    buttons = get_user_btn(user)
    buttons_code = dict()
    # for page_code, _btn in buttons.items():
    #     buttons_code[page_code] = [item['code'] for item in _btn]

    for item in query_pms:
        if item.code not in buttons_code:
            buttons_code[item.code] = []

    results['group'] = acs
    results['page'] = pms
    results['buttons'] = buttons
    return Response(data=results)
