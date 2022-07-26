"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import data_export.api
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.conf.urls import url
from rest_framework.routers import DefaultRouter


# 增加promt - api.py
from . import api, views, prompt_api
from .api_set import ProjectSetViews
app_name = 'projects'

# collections
_collections_urlpatterns = [
    path('', views.project_collection, name='project-index'),
]

# reverse for projects:name
_urlpatterns = [
    path('', views.project_list, name='project-index'),
    path('collection', views.project_list, name='project-index'),
    path('<int:pk>/settings/', views.project_settings, name='project-settings', kwargs={'sub_path': ''}),
    path('<int:pk>/settings/<sub_path>', views.project_settings, name='project-settings-anything'),

    path('upload-example/', views.upload_example_using_config, name='project-upload-example-using-config'),
]

# reverse for projects:api:name
_api_urlpatterns = [
    # CRUD
    path('', api.ProjectListAPI.as_view(), name='project-list'),
    path('<int:pk>/', api.ProjectAPI.as_view(), name='project-detail'),

    # Get next task
    path('<int:pk>/next/', api.ProjectNextTaskAPI.as_view(), name='project-next'),

    # Validate label config in general
    path('validate/', api.LabelConfigValidateAPI.as_view(), name='label-config-validate'),

    # Validate label config for project
    path('<int:pk>/validate/', api.ProjectLabelConfigValidateAPI.as_view(), name='project-label-config-validate'),

    # Project summary
    path('<int:pk>/summary/', api.ProjectSummaryAPI.as_view(), name='project-summary'),

    # Tasks list for the project: get and destroy
    path('<int:pk>/tasks/', api.ProjectTaskListAPI.as_view(), name='project-tasks-list'),

    # Generate sample task for this project
    path('<int:pk>/sample-task/', api.ProjectSampleTask.as_view(), name='project-sample-task'),

    # List available model versions
    path('<int:pk>/model-versions/', api.ProjectModelVersions.as_view(), name='project-model-versions'),

]


_api_urlpatterns_templates = [
    path('', api.TemplateListAPI.as_view(), name='template-list'),
]

router = DefaultRouter(trailing_slash=False)
router.register(r'', ProjectSetViews, basename='project set')
_api_url_set_patterns = [
    path('', include(router.urls)),
]

urlpatterns = [
    path('projects/', include(_urlpatterns)),
    path('collections/', include(_collections_urlpatterns)),
    path('api/projects/', include((_api_urlpatterns, app_name), namespace='api')),
    path('api/project-set/', include((_api_url_set_patterns, app_name), namespace='api-set')),
    path('api/templates/', include((_api_urlpatterns_templates, app_name), namespace='api-templates')),

    # 推断学习模版curd
    path('api/templates/prompt-learning/', prompt_api.PromptAPI.as_view()),
    path('api/templates/prompt-learning/<int:project>/', prompt_api.PromptAPI.as_view(), name='template-detail-get'),
    path('api/templates/prompt-learning/<int:id>/', prompt_api.PromptAPI.as_view(), name='template-detail-update'),

    # 增加两个关于推断学习算法的接口
    path('api/projects/prompt-learning/predict/', prompt_api.PromptLearning.as_view()),
    # re_path(r'api/projects/prompt-learning/retrieve?project=(\d+)&&taskId=(\d+)', prompt_api.PromptExport.as_view()),
    path(r'api/projects/prompt-learning/retrieve', prompt_api.PromptExport.as_view()),
]
