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
        'NAME': 'label_studio',
        'HOST': '192.168.0.92',
        'PORT': '5432',
    }
}


RQ_QUEUES = {
    'default': {
        'HOST': '127.0.0.1',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 18000,
    },
    'pre_tags': {
        'HOST': '127.0.0.1',
        'PORT': 6379,
        'DB': 1,
        'DEFAULT_TIMEOUT': 18000,
    },
    'algorithm_clean': {
        'HOST': '127.0.0.1',
        'PORT': 6379,
        'DB': 1,
        'DEFAULT_TIMEOUT': 18000,
    },
    'prompt': {
        'HOST': '127.0.0.1',
        'PORT': 6379,
        'DB': 1,
        'DEFAULT_TIMEOUT': 18000,
    },
}
