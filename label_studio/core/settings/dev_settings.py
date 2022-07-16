#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : jindu_settings.py
  > CreateTime : 2022/6/20 08:41
"""

DATABASES = {
    'default':  {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'root',
        'PASSWORD': 'linshimima2!',
        'NAME': 'label_studio_dev',
        'HOST': '124.71.161.146',
        'PORT': '5432',
    }
}


RQ_QUEUES = {
    'default': {
        'HOST': 'redis-dev',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 18000,
    },
    'prediction': {
        'HOST': 'redis-dev',
        'PORT': 6379,
        'DB': 1,
        'DEFAULT_TIMEOUT': 3600 * 24 * 2,
    },
    'algorithm_clean': {
        'HOST': 'redis-dev',
        'PORT': 6379,
        'DB': 1,
        'DEFAULT_TIMEOUT': 3600 * 24 * 2,
    },
    'prompt': {
        'HOST': 'redis-dev',
        'PORT': 6379,
        'DB': 1,
        'DEFAULT_TIMEOUT': 18000,
    },
}
