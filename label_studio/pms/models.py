#!/usr/bin/env python
# encoding: utf-8

"""
  > FileName   : models.py
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > CreateTime : 2022-05-05 15:43
"""
from datetime import datetime
from django.db.models import SET_NULL
from django.db.models import CharField
from django.db.models import ForeignKey
from django.db.models import DO_NOTHING
from django.db.models import DateTimeField
from django.db.models import ManyToManyField
from django.db.models import IntegerField
from django.db.models import BooleanField
from django.db.models import SmallIntegerField
from django.contrib.auth.models import Group
from django.db.models import Model
from users.models import User


class PmsPage(Model):
    """
    前端页面
    code 前三位是一级菜单，第二个三位是二级菜单，第三个三位是三级菜单
    """
    code = CharField(max_length=50, unique=True)
    title = CharField(max_length=50, verbose_name='菜单标题')
    name = CharField(max_length=50, blank=True, null=True, verbose_name='菜单别名')
    path = CharField(max_length=100, blank=True, null=True, verbose_name='菜单路径')
    icon = CharField(max_length=40, null=True, blank=True, verbose_name='图标')
    remark = CharField(max_length=100, null=True, blank=True, verbose_name="备注")
    project = CharField(max_length=30, null=True, blank=True, verbose_name='项目')

    group = ManyToManyField(to=Group, verbose_name='组', related_name='pms_group', blank=True)
    user = ManyToManyField(to=User, verbose_name='用户', related_name='pms_user', blank=True)

    created_at = DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = DateTimeField(null=True, blank=True, auto_now=True)
    created_by = ForeignKey(User, related_name='%(class)s_created_by_user', null=True, blank=True, db_index=True, on_delete=SET_NULL)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super(Model, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        kwargs['updated_at'] = datetime.now()
        if self._state.adding:
            raise self.DoesNotExist
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save(update_fields=kwargs.keys())

    class Meta:
        db_table = 'pms_page'
        verbose_name = '菜单页面'
        verbose_name_plural = verbose_name


# 按键表
class PmsButton(Model):
    """
    """
    name = CharField(max_length=30)
    code = CharField(max_length=20)  # unique
    page = ForeignKey(PmsPage, verbose_name='页面',
                      related_name='pms_btn_page', on_delete=DO_NOTHING,
                      blank=True)
    remark = CharField(max_length=100, null=True, blank=True, verbose_name=u"备注")

    group = ManyToManyField(to=Group, verbose_name='组', related_name='pms_btn_group', blank=True)
    user = ManyToManyField(to=User, verbose_name='用户', related_name='pms_btn_user', blank=True)

    class Meta:
        db_table = 'pms_page_button'
        verbose_name = '菜单页面按键'
        verbose_name_plural = verbose_name
        unique_together = (
            ('page', 'code'),
        )
