#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : __init__.py
  > CreateTime : 2022/6/7 16:53
"""

from db_ml.listener_result import RedisSpaceListener
from core.redis import _redis

listener = RedisSpaceListener(_redis)
listener.start()
