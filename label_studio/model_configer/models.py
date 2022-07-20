"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import json
import logging

from django.db.models import Q, Avg, Count, Sum, Value, BooleanField, Case, When
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import transaction, models
from annoying.fields import AutoOneToOneField
from functools import lru_cache

from core.redis import start_job_async_or_sync
from tasks.models import Task, Prediction, Annotation, Q_task_finished_annotations, bulk_update_stats_project_tasks
from core.utils.common import create_hash, get_attr_or_item, load_func
from core.utils.exceptions import LabelStudioValidationErrorSentryIgnored
from core.label_config import (
    validate_label_config,
    extract_data_types,
    get_all_object_tag_names,
    config_line_stipped,
    get_sample_task,
    get_all_labels,
    get_all_control_tag_tuples,
    get_annotation_tuple,
)
from core.bulk_update_utils import bulk_update
from label_studio_tools.core.label_config import parse_config
from core.mixins import DummyModelMixin


logger = logging.getLogger(__name__)


MODEL_TYPE = (
    ('intention', '对话意图分类'),
    ('generation', '对话生成'),
    ('clean', '清洗模型'),
    ('other', '其他'),
)


class ModelConfigerManager(models.Manager):
    def for_user_organization(self, user):
        return self.filter(organization=user.active_organization)


class ModelConfiger(DummyModelMixin, models.Model):
    objects = ModelConfigerManager()

    title = models.CharField(_('title'), null=True, blank=True, default='', max_length=200, help_text='Model name.')
    url = models.TextField(_('url'), unique=True, help_text='URL for the machine learning model server')
    description = models.TextField(_('description'), blank=True, null=True, default='', help_text='model configer description')
    token = models.CharField(_('token'), max_length=65, default=create_hash, unique=True, null=True, blank=True)

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='model_configer', null=True)
    version = models.TextField(_('model version'), blank=True, null=True, default='', help_text='Machine learning model version')
    type = models.CharField(_('model type'), choices=MODEL_TYPE, default='other', null=True, max_length=50)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_model', on_delete=models.SET_NULL, null=True, verbose_name=_('created by'))
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    # 项目集合先保留 项目集合在添加外键
    #  录入模型的模型名字 训练用的项目名称
    model = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, help_text='训练用的基础模型', related_name='model_config')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, help_text='训练用的项目', related_name='model_config_project')
