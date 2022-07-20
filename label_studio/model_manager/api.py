"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import drf_yasg.openapi as openapi
import logging
import numpy as np
import pathlib
import os

from django.db import IntegrityError
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from rest_framework import generics, status, filters
from rest_framework.exceptions import NotFound, ValidationError as RestValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import exception_handler
from django.http import Http404

from core.utils.common import temporary_disconnect_all_signals
from core.label_config import config_essential_data_has_changed
from projects.models import (
    Project, ProjectSummary, ProjectManager
)
from projects.serializers import (
    ProjectSerializer, ProjectLabelConfigSerializer, ProjectSummarySerializer
)
from projects.functions.next_task import get_next_task
from tasks.models import Task
from tasks.serializers import TaskSerializer, TaskSimpleSerializer, TaskWithAnnotationsAndPredictionsAndDraftsSerializer, NextTaskSerializer
from webhooks.utils import api_webhook, api_webhook_for_delete, emit_webhooks_for_instance
from webhooks.models import WebhookAction

from core.permissions import all_permissions, ViewClassPermission
from core.utils.common import (
    get_object_with_check_and_log, paginator, paginator_help)
from core.utils.exceptions import ProjectExistException, LabelStudioDatabaseException
from core.utils.io import find_dir, find_file, read_yaml

from data_manager.functions import get_prepared_queryset, filters_ordering_selected_items_exist
from data_manager.models import View

logger = logging.getLogger(__name__)
