#!/usr/bin/env python
# encoding: utf-8

"""
  > FileName   : services.py
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > CreateTime : 2022/6/18 14:44
"""
import re
from pms.models import PmsPage
from pms.models import PmsButton
from django.db.models import Q
from django.contrib.auth.models import User, Group
from pms.group_serializer import GroupListSerializer

SINGLE_LAYER_MENU_LENGTH = 3


def generate_code(parent_code: str, project: str) -> (bool, str):
    """

    :param parent_code:
    :param project:
    :return:
    """
    if parent_code:
        exists = PmsPage.objects.filter(code=parent_code).all()
        if not exists:
            return False, 'Not Query ParentCode'
        query = PmsPage.objects.filter(
            project=project, code__startswith=parent_code
        ).values('id', 'code').order_by('-code')
        if len(query) == 1:
            return True, parent_code + '001'
        else:
            same_query = [
                item for item in query if len(item['code']) == len(parent_code)
                + SINGLE_LAYER_MENU_LENGTH
            ]
            reg_str = '.{' + str(SINGLE_LAYER_MENU_LENGTH) + '}'
            codes = re.findall(reg_str, same_query[0]['code'])
            code = str(int(codes[-1]) + 1).zfill(SINGLE_LAYER_MENU_LENGTH)
            new_code = ''.join(codes[:-1]) + code
            return True, new_code
    else:
        query = PmsPage.objects.filter(project=project)\
            .values('id', 'code').order_by('-code')
        if not query:
            return True, '001'
        else:
            same_query = [
                item for item in query
                if len(item['code']) == SINGLE_LAYER_MENU_LENGTH
            ]
            code = str(int(same_query[0]['code']) + 1).zfill(
                SINGLE_LAYER_MENU_LENGTH
            )
            return True, code


def generate_btn_code(page: PmsPage) -> str:
    """
    :param page:
    :return:
    """
    query = PmsButton.objects.filter(page=page).values(
        'id', 'code').order_by('-code')
    if not query:
        return '001'
    else:
        return str(int(query.first()['code']) + 1).zfill(
            SINGLE_LAYER_MENU_LENGTH)


def is_admin(groups):
    """
    判断admin用户
    :param groups:
    :return:
    """
    for item in groups:
        if 'admin' in item.name:
            return True
    return False


def user_group_query(user, pms_model, pms_type='all'):
    """
    pms_model   PmsButton or PmsPage
    :param user:
    :param pms_model:
    :param pms_type:
    :return:
    """
    query = pms_model.objects.all()
    groups = user.groups.all()

    #
    if is_admin(groups=groups):
        return query

    if pms_type == 'user':
        query = query.filter(user=user)
    elif pms_type == 'group':
        query = query.filter(Q(group__in=groups))
    else:
        query = query.filter(Q(user=user) | Q(group__in=groups))

    return query


def get_user_btn(user):
    """

    :param access:
    :param user:
    :return:
    """
    query_btn = user_group_query(user, PmsButton)
    query_vls = query_btn.values('name', 'code', 'page__code').all()
    results = dict()
    for item in query_vls:
        page_code = item.pop('page__code')
        if page_code in results:
            btn = results[page_code]
            btn.append(item)
            results[page_code] = btn
        else:
            results[page_code] = [item]
    return results


def check_params(data):
    """
    检查参数
    :param data:
    :return:
    """
    user_id = data.get('user')
    group_id = data.get('group')

    if not user_id and not group_id:
        return False, '必须包含用户或是用户组'

    return True, (user_id, group_id, data)


def set_menu_pms(data, user_id, group_id=None, opt='add'):
    """
    父菜单不进行权限设置，减少前端代码
    :param data:
    :param user_id:
    :param group_id:
    :param opt:
    :return:
    """
    # children = data.get('children')
    # if children:
    #     for item in children:
    #         set_menu_pms(item, user_id=user_id, group_id=group_id)
    #
    # if not len(children):
    page_ids = data.get('page')
    queryset = PmsPage.objects.filter(code__in=page_ids)
    if user_id:
        query_user = queryset.filter(user=user_id)
        update_menu(queryset, query_user, opt, uid=user_id)
    elif group_id:
        query_group = queryset.filter(group=group_id)
        update_menu(queryset, query_group, opt, gid=group_id)


def update_menu(query_page, query_pms, opt, uid=None, gid=None) -> int:
    count = 0
    if opt == 'add':
        for query in query_page:
            if len(query_pms) and query.id == query_pms[0].id:
                continue

            if uid:
                query.user.add(uid)
                count += 1
            elif gid:
                query.group.add(gid)
                count += 1
    elif opt == 'remove':
        for query in query_page:
            if not len(query_pms) or query.id != query_pms[0].id:
                continue

            if uid:
                query.user.remove(uid)
                count += 1
            elif gid:
                query.group.remove(gid)
                count += 1
    return count


def join_menu(menu, desc=[], level=1):
    layer = SINGLE_LAYER_MENU_LENGTH * level
    menu_id = menu.get('code')
    next_menu_id = menu_id[layer:]
    parent_id = menu_id[:layer+3]
    if len(next_menu_id) == SINGLE_LAYER_MENU_LENGTH:
        menu['children'] = []
        if desc:
            desc.append(menu)
        else:
            desc = [menu]
        return desc
    else:
        for _index, _item in enumerate(desc):
            if parent_id != str(_item.get('code')):
                continue
            desc[_index]['children'] = join_menu(
                menu, _item.get('children'),
                level=int(len(parent_id)/SINGLE_LAYER_MENU_LENGTH)
            )
        return desc


def update_auth_btn(request, opt):
    """
        更新菜单按键
        :param request:
        :param opt:
        :return:
        """
    state, results = check_params(request.data)
    if not state:
        return False, results

    user_id, group_id, data = results
    btn_id = data.get('btn')

    queryset = PmsButton.objects.filter(id__in=btn_id)

    # opt: add & remove
    count = 0
    if user_id:
        query_user = queryset.filter(user=user_id)
        count = update_menu(queryset, query_user, opt, uid=user_id)
    elif group_id:
        query_group = queryset.filter(group=group_id)
        count = update_menu(queryset, query_group, opt, gid=group_id)
    return True, f'更新成功{count}条记录'


def update_auth_page_or_btn(request, model_cls, params_field):
    state, results = check_params(request.data)
    if not state:
        return False, results
    user_id, group_id, data = results

    update_ids = data.get(params_field)
    del_count, add_count = 0, 0
    if user_id:
        user = User.objects.filter(id=user_id).first()
        queryset = model_cls.objects.filter(user=user)
        exists_ids = [item.id for item in queryset]
        remove_ids = list(set(exists_ids).difference(set(update_ids)))
        wait_add_ids = list(set(update_ids).difference(set(exists_ids)))
        for g in model_cls.objects.filter(id__in=remove_ids):
            g.user.remove(user)
            del_count += 1
        for g in model_cls.objects.filter(id__in=wait_add_ids):
            g.user.add(user)
            add_count += 1
    elif group_id:
        group = Group.objects.filter(id=group_id).first()
        queryset = model_cls.objects.filter(group=group)

        exists_ids = [item.id for item in queryset]
        remove_ids = list(set(exists_ids).difference(set(update_ids)))
        wait_add_ids = list(set(update_ids).difference(set(exists_ids)))
        for g in model_cls.objects.filter(id__in=remove_ids):
            g.group.remove(group)
            del_count += 1
        for g in  model_cls.objects.filter(id__in=wait_add_ids):
            g.group.add(group)
            add_count += 1

    return True, f'更新成功,移除{del_count}条记录,更新{add_count}条记录。'


def get_user_auth(user: User) -> dict:
    results = dict()
    groups = user.groups.all()
    group_serializer = GroupListSerializer(instance=groups, many=True)
    results['groups'] = group_serializer.data

    # 按键
    user.pms_btn_user.all()

    # 菜单


def user_access(user):
    # 添加默认用户组
    # 用户加入用户组user.groups.add(group)
    # 或group.user_set.add(user)

    # if user.username in ('admin', ):
    #     return ['admin']

    if not user.groups.exists():
        guest_group, is_created = Group.objects.get_or_create(name='guest')
        if is_created:
            user.groups.add(guest_group)

    access = []
    for item in user.groups.all():
        access.append(item.name)
    return access


if __name__ == '__main__':
    pass

