#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : yjd_settings.py
  > CreateTime : 2022/7/18 13:52
"""

DATABASES = {
    'default':  {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'root',
        'PASSWORD': 'linshimima2!',
        'NAME': 'label_studio_dev',
        'HOST': '123.60.43.172',
        'PORT': '5432',
    }

# 'default':  {
#         'ENGINE': 'django.db.backends.postgresql',
#         'USER': 'postgres',
#         'PASSWORD': 'Dbtest',
#         'NAME': 'label_studio_dev',
#         'HOST': '49.234.42.225',
#         'PORT': '5432',
#     }
}


RQ_QUEUES = {
    'default': {
        'HOST': '124.71.161.146',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 18000,
    },
    'prediction': {
        'HOST': '124.71.161.146',
        'PORT': 6379,
        'DB': 1,
        'DEFAULT_TIMEOUT': 3600 * 24 * 2,
    },
    'algorithm_clean': {
        'HOST': '124.71.161.146',
        'PORT': 6379,
        'DB': 1,
        'DEFAULT_TIMEOUT': 3600 * 24 * 2,
    },
    'prompt': {
        'HOST': '124.71.161.146',
        'PORT': 6379,
        'DB': 1,
        'DEFAULT_TIMEOUT': 18000,
    },
}