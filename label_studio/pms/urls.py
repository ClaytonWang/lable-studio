#!/usr/bin/env python
# encoding: utf-8

"""
  > FileName   : urls.py
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > CreateTime : 2022-04-11 15:29
"""


from django.conf.urls import include, url
from django.urls import path
from rest_framework.routers import DefaultRouter

from pms.views import user_info
from .page_views import PmsPageViews
from .button_view import PmsBtnViews
from .views import menu_tree
from .group_views import GroupViews


router = DefaultRouter(trailing_slash=False)
router.register(r'page', PmsPageViews, basename='pms_page')
router.register(r'btn', PmsBtnViews, basename='pms_btn')
router.register(r'group', GroupViews, basename='pms_group')

urlpatterns = [
    path(r'pms/', include(router.urls)),
    path(r'pms/get_info', user_info),
    path(r'pms/menu/tree', menu_tree),
]
