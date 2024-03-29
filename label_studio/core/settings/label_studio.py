"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from core.settings.base import *

DJANGO_DB = get_env('DJANGO_DB', DJANGO_DB_POSTGRESQL)
DATABASES = {'default': DATABASES_ALL[DJANGO_DB]}

MIDDLEWARE.append('organizations.middleware.DummyGetSessionMiddleware')
MIDDLEWARE.append('core.middleware.UpdateLastActivityMiddleware')

ADD_DEFAULT_ML_BACKENDS = False

LOGGING['root']['level'] = get_env('LOG_LEVEL', 'WARNING')

DEBUG = get_bool_env('DEBUG', False)

DEBUG_PROPAGATE_EXCEPTIONS = get_bool_env('DEBUG_PROPAGATE_EXCEPTIONS', False)

SESSION_COOKIE_SECURE = False

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

REDIS_HOST = get_env('REDIS_HOST', '127.0.0.1')
REDIS_PORT = get_env('REDIS_PORT', 6379)
RQ_QUEUES = {
    'default': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': 0,
        'DEFAULT_TIMEOUT': 18000,
    },
    'prediction': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': 1,
        'DEFAULT_TIMEOUT': 3600 * 24 * 2,
    },
    'algorithm_clean': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': 1,
        'DEFAULT_TIMEOUT': 3600 * 24 * 2,
    },
    'prompt': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': 1,
        'DEFAULT_TIMEOUT': 18000,
    },
}

SENTRY_DSN = get_env(
    'SENTRY_DSN',
    'http://88b0a9b1ab8d4d1cad75d981676eacad@124.71.161.146:9000/2'
)
SENTRY_ENVIRONMENT = get_env('SENTRY_ENVIRONMENT', 'opensource')

FRONTEND_SENTRY_DSN = get_env(
    'FRONTEND_SENTRY_DSN',
    'http://88b0a9b1ab8d4d1cad75d981676eacad@124.71.161.146:9000/2')
FRONTEND_SENTRY_ENVIRONMENT = get_env('FRONTEND_SENTRY_ENVIRONMENT', 'opensource')

EDITOR_KEYMAP = json.dumps(get_env("EDITOR_KEYMAP"))

from label_studio import __version__
from label_studio.core.utils import sentry
sentry.init_sentry(release_name='label-studio', release_version=__version__)

# we should do it after sentry init
from label_studio.core.utils.common import collect_versions
versions = collect_versions()

# in Label Studio Community version, feature flags are always ON
FEATURE_FLAGS_DEFAULT_VALUE = True

# 模型训练时间
MODEL_TRAIN_INDIVIDUAL_TASK_TIME = 0.25
# 注册有效时间是2天
SIGNUP_INVITE_EXPIRE_TIME = 60 * 60 * 24 * 2
# 系统分组，不能进行删除和编辑
SYSTEM_GROUP = ['admin', 'user', 'annotator']
MODEL_SERVING_HOST = 'http://192.168.0.216:12000'
# 增加配置文件
ENV = os.getenv('ENV', '').upper()
if 'DEV' == ENV:
    from core.settings.dev_settings import *
elif 'QA' == ENV:
    from core.settings.qa_settings import *
elif 'YJD' == ENV:
    from core.settings.yjd_settings import *
else:
    pass
