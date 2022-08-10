#!/usr/bin/env python
# encoding: utf-8

"""
  > FileName: serializer.py
  > Author: Yin
  > Mail: jindu.yin@digitalbrain.cn
  > CreatedTime: 2022/04/17 17:05
"""

from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SerializerMethodField
from rest_framework.serializers import CharField
from .models import PmsPage
from .models import PmsButton

