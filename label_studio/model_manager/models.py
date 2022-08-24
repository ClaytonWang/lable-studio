"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import json
import logging

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import transaction, models
from core.utils.common import create_hash, get_attr_or_item, load_func
from core.mixins import DummyModelMixin
from db_ml.common import DbOrganizationManager


logger = logging.getLogger(__name__)


MODEL_TYPE = (
    ('intention', '对话意图分类'),
    ('generation', '对话生成'),
    ('clean', '清洗模型'),
    # ('other', '其他'),
)

MODEL_STATE = (
    (1, '初始'),
    (2, '评估'),
    (3, '训练'),
    (4, '完成'),
    (5, '异常'),
)


MODEL_TRAIN_TYPE = (
    ('train', '训练'),
    ('assessment', '评估'),
)


class ModelManager(DummyModelMixin, models.Model):

    objects = DbOrganizationManager()

    # title 模型集名称，模型名称是模型集名称 + 版本
    title = models.CharField(_('title'), max_length=20, help_text='Model set name. ')
    url = models.TextField(_('url'), unique=True, help_text='URL for the machine learning model server')
    description = models.TextField(_('description'), blank=True, null=True, default='', help_text='model configer description')
    token = models.CharField(_('token'), max_length=65, default=create_hash, null=True, blank=True)

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='model_configer', null=True)
    version = models.TextField(_('model version'), blank=True, null=True, default='1.0', help_text='Machine learning model version')
    type = models.CharField(_('model type'), choices=MODEL_TYPE, default=None, null=True, max_length=50)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_model', on_delete=models.SET_NULL, null=True, verbose_name=_('created by'))
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    # 基于 指定模型的训练
    model = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, help_text='训练用的基础模型', related_name='model_config')
    # 项目预留外建，追溯模型训练的项目信息
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, help_text='训练用的项目', related_name='model_config_project')
    # 项目集
    project_set = models.ForeignKey('projects.ProjectSet', on_delete=models.SET_NULL, null=True, blank=True, help_text='项目集合', related_name='model_config_project_set')

    # 模型参数 模型调用参数和标签都放在这里
    # 这仨个放这作用不是很大，先不删了。
    state = models.IntegerField(_('model state'), choices=MODEL_STATE, default=1, null=True)
    model_parameter = JSONField(_('run model parameter'), null=True, default=dict, help_text='模型入参数')
    model_result = models.CharField(_('run model result url'), null=True, default='', max_length=140, help_text='模型入参数')

    class Meta:
        unique_together = ("organization_id", "title", "version")


class ModelTrain(models.Model):
    """
    人在环路-训练记录
    """
    objects = DbOrganizationManager()

    # 组织
    organization = models.ForeignKey('organizations.Organization', on_delete=models.SET_NULL, related_name='model_record_org', null=True)
    # 训练前模型
    model = models.ForeignKey('model_manager.ModelManager', on_delete=models.SET_NULL, null=True, blank=True, help_text='', related_name='model_record')
    # 新模型
    new_model = models.ForeignKey('model_manager.ModelManager', on_delete=models.SET_NULL, null=True, blank=True)
    # 项目
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, help_text='', related_name='model_record_project')

    # 正确标注数
    exactness_count = models.IntegerField(_('exactness annotation'), default=0, null=True)
    # 总任务数
    total_count = models.IntegerField(_('total task'), default=0, null=True)
    # 是否训练
    is_train = models.BooleanField(_('train'), default=False)
    # 准确率
    accuracy_rate = models.FloatField(_('accuracy rate'), null=True, blank=True, default=0)
    # 新模型准确率
    new_accuracy_rate = models.FloatField(_('new accuracy rate'), null=True, blank=True, default=0)
    # 新模型训练任务数
    new_model_train_task = models.IntegerField('', null=True, blank=True, default=None)
    # 新模型评估任务数
    new_model_assessment_task = models.IntegerField('', null=True, blank=True, default=None)
    # 训练进度
    training_progress = models.FloatField('', null=True, blank=True, default=None)
    # 分类 训练&评估
    category = models.CharField('', max_length=15, choices=MODEL_TRAIN_TYPE)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_project_record', on_delete=models.SET_NULL, null=True, verbose_name=_('created by'))
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='updated_project_record', on_delete=models.SET_NULL, null=True, verbose_name=_('updated by'))

    # 模型参数 模型调用参数和标签都放在这里
    state = models.IntegerField(_('model state'), choices=MODEL_STATE, default=1, null=True)
    model_parameter = JSONField(_('run model parameter'), null=True, default=dict, help_text='模型入参数')
    model_result = models.CharField(_('run model result url'), null=True, default='', max_length=140, help_text='模型训练结果URL')

    def has_permission(self, user):
        return self.organization == user.active_organization
