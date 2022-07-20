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


logger = logging.getLogger(__name__)
