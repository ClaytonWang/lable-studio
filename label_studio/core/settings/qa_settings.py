#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : qa_settings.py
  > CreateTime : 2022/7/11 09:24
"""


DATABASES = {
    'default':  {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'root',
        'PASSWORD': 'linshimima2!',
        'NAME': 'label_studio_qa',
        'HOST': '192.168.0.92',
        'PORT': '5432',
    }
}

RQ_QUEUES = {
    'default': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 18000,
    },
    'prediction': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 1,
        'DEFAULT_TIMEOUT': 3600 * 24 * 2,
    },
    'algorithm_clean': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 1,
        'DEFAULT_TIMEOUT': 3600 * 24 * 2,
    },
    'prompt': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 1,
        'DEFAULT_TIMEOUT': 18000,
    },
}