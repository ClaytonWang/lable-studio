#! /usr/bin/env python3
"""
Created by liuhengxin
"""

from rest_framework.response import Response
from label_studio.ml.prompt_ml import patch_prompt
from rest_framework import permissions
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from .models import PromptResult, PromptTemplates, PromptResultDraft
from tasks.models import Task
from projects.models import Project
from core.redis import start_job_async_or_sync
from db_ml.services import save_raw_data
from db_ml.services import PROMPT_BACKUP_FIELDS
from db_ml.services import generate_redis_key
from core.redis import redis_set, redis_get
from db_ml.services import AlgorithmState
from db_ml.services import predict_prompt
from db_ml.services import generate_uuid
from db_ml.services import redis_set_json, redis_get_json
from db_ml.services import get_project_labels
from db_ml.services import cut_task_to_model
from db_ml.services import query_last_record
from db_ml.services import create_model_record
from db_ml.listener_result import thread_read_redis_celery_result


class PromptLearning(APIView):
    """
        增加提示学习模型调用接口
    """
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response('hello prompt-learning', status=status.HTTP_200_OK)

    # def post(self, request, *args, **kwargs):
    #     params = request.data
    #     print('params', params)
    #     try:
    #         result = patch_prompt(params['templates'], params['task'])
    #         print('result', result)
    #         # 入库
    #         c = PromptResult.objects.create(project_id=params['project'], task_id=params['taskId'], metrics=result)
    #         c.save()
    #         result = {'status': 0, 'error': ''}
    #         resp_status = status.HTTP_200_OK
    #     except Exception as e:
    #         result = {'status': 0, 'error': str(e)}
    #         resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    #     return Response(result, status=resp_status)

    def post(self, request, *args, **kwargs):
        """
        提示学习的触发入口
        """
        params = request.data
        print('params', params)
        project_id = params['project_id']
        model_id = params.get('model_id', None)

        if query_last_record(project_id):
            return Response(status=400, data=dict(msg='Project is running model.'))

        try:
            # 获取templates
            template_list = PromptTemplates.objects.filter(project_id=project_id).values()
            # print('template_list', template_list)
            templates = [item['template'] for item in template_list]
            # 获取tasks
            tasks = Task.objects.filter(project_id=project_id).values()
            if not tasks:
                return Response(status=400, data=dict(msg='Invalid project id'))

            if PromptResultDraft.objects.filter(project_id=project_id).exists():
                PromptResultDraft.objects.filter(project_id=project_id).delete()

            record_status, record = create_model_record(model_id, project_id, request.user)
            if not record_status:
                return Response(status=400, data=dict(msg='Invalid model id.'))

            # 清空project_id对应的PromptResult表
            c = PromptResult.objects.filter(project_id=project_id).all()
            if len(c):
                save_raw_data(c, PromptResultDraft, PROMPT_BACKUP_FIELDS)
                PromptResult.objects.filter(project_id=project_id).delete()

            project = Project.objects.filter(id=project_id).first()
            _uuid = generate_uuid('prompt', record.id)
            state, result = None, None
            for sub_query in cut_task_to_model(tasks):
                task_data = []
                for task in sub_query:
                    dialogue = task.get('data', {}).get('dialogue', [])
                    task_data.append(dict(
                        task_id=task.get('id'),
                        dialogue=dialogue
                    ))

                if project.template_type == 'intent-classification':
                    state, result = predict_prompt(
                        project_id, model_id, task_data, _uuid, templates,
                        prompt_type='intent-classification',
                    )
                elif project.template_type == 'conversational-generation':
                    # 对话生产
                    labels = get_project_labels(project_id)
                    if len(labels):
                        generate_count = params.get('generate_count', 1)
                        state, result = predict_prompt(
                            project_id, model_id, task_data, _uuid, templates,
                            return_num=generate_count,
                            prompt_type='conversational-generation',
                        )
                    else:
                        state = False
                        result = '项目未设置标签'

                if not state:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={'status': 1, 'error': result})

            result = {'status': 0, 'error': ''}
            resp_status = status.HTTP_200_OK
            thread_read_redis_celery_result(project_id, 'prompt', record)
        except Exception as e:
            result = {'status': 1, 'error': str(e)}
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(result, status=resp_status)


class PromptExport(APIView):
    """
        提示学习输出接口
    """
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        params = request.GET.dict()
        print('get params', params)
        try:
            c = PromptResult.objects.filter(project_id=params['project']).filter(task_id=params['taskId']).values()
            result = c[0]['metrics'] if len(c) else []
            resp_status = status.HTTP_200_OK
        except Exception as e:
            result = str(e)
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(result, status=resp_status)

    # def post(self, request, *args, **kwargs):
    #     params = request.data
    #     print('params', params)
    #     try:
    #         c = PromptResult.objects.filter(project_id=params['project']).filter(task_id=params['taskId']).values()
    #         result = c[0]['metrics']
    #         resp_status = status.HTTP_200_OK
    #     except Exception as e:
    #         result = str(e)
    #         resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    #     return Response(result, status=resp_status)


@method_decorator(name='post', decorator=swagger_auto_schema(
        tags=['Prompt-learning'],
        operation_summary='Create prompt template',
        operation_description='Create prompt template by project ID and task ID.'
    ))
@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Prompt-learning'],
        operation_summary='Get prompt template',
        operation_description='Retrieve prompt template by project ID and task ID.'
    ))
@method_decorator(name='delete', decorator=swagger_auto_schema(
        tags=['Prompt-learning'],
        operation_summary='Delete prompt template',
        operation_description='Delete a prompt template by project ID and task ID.'
    ))
@method_decorator(name='patch', decorator=swagger_auto_schema(
        tags=['Prompt-learning'],
        operation_summary='Update prompt template',
        operation_description='Update prompt template partially by project ID and task ID.',
        # request_body=ProjectSerializer
    ))
@method_decorator(name='put', decorator=swagger_auto_schema(
        tags=['Prompt-learning'],
        operation_summary='Update prompt template overall',
        operation_description='Update prompt template by project ID and task ID.',
        # request_body=ProjectSerializer
    ))
class PromptAPI(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [permissions.AllowAny]
    # permission_classes = [permissions.IsAuthenticated]
    # permission_required = ViewClassPermission(
    #     GET=all_permissions.projects_view,
    #     DELETE=all_permissions.projects_delete,
    #     PATCH=all_permissions.projects_change,
    #     PUT=all_permissions.projects_change,
    #     POST=all_permissions.projects_create,
    # )

    # queryset = Project.objects.with_counts()

    # create
    def post(self, request, *args, **kwargs):
        params = request.data
        try:
            c = PromptTemplates.objects.create(
                project_id=params['project'], template=params['template']
            )
            c.save()
            result = {'status': 0, 'error': ''}
            resp_status = status.HTTP_200_OK
        except Exception as e:
            result = {'status': 1, 'error': f'{e}'}
            resp_status = status.HTTP_200_OK
        return Response(result, status=resp_status)

    # read
    def get(self, request, *args, **kwargs):
        project_id = kwargs.get('project')
        print('project_id', project_id)
        ts = PromptTemplates.objects.filter(project_id=project_id).values()
        # import pdb
        # pdb.set_trace()
        # print('ts', ts)
        # transform
        # result = [item['template'] for item in ts]
        result = [{'template': item['template'], 'id': item['id']} for item in ts]
        print('result', result)
        # return Response(result, status=status.HTTP_200_OK)
        return Response({'templates': result}, status=status.HTTP_200_OK)

    # # delete
    # def delete(self, request, *args, **kwargs):
    #     params = request.data
    #     print('params', params)
    #     try:
    #         c = PromptTemplates.objects.filter(project_id=params['project']).filter(template=params['template'])
    #         c.delete()
    #         result = {'status': 0, 'error': ''}
    #         resp_status = status.HTTP_200_OK
    #     except Exception as e:
    #         print('e', e)
    #         result = {'status': 1, 'error': e}
    #         resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    #     return Response(result, status=resp_status)

    # delete
    def delete(self, request, *args, **kwargs):
        params = request.data
        print('params', params)
        try:
            c = PromptTemplates.objects.filter(id=params['id'])
            c.delete()
            result = {'status': 0, 'error': ''}
            resp_status = status.HTTP_200_OK
        except Exception as e:
            print('e', e)
            result = {'status': 1, 'error': e}
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(result, status=resp_status)

    # 部分update
    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)

    # def get_queryset(self):
    #     return PromptTemplates.objects.filter(project_id=self.request.data.get('project')).\
    #         filter(template=self.request.data.get('template'))
    #
    # #  put must queryset or get_queryset
    # # @swagger_auto_schema(auto_schema=None)
    # def put(self, request, *args, **kwargs):
    #     params = request.data
    #     try:
    #         c = self.get_queryset()
    #         print('c', c)
    #         c.update(template=params['new'])
    #         result = {'status': 0, 'error': ''}
    #         resp_status = status.HTTP_200_OK
    #     except Exception as e:
    #         result = {'status': 1, 'error': str(e)}
    #         resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    #     return Response(result, status=resp_status)

    def get_queryset(self, idx):
        return PromptTemplates.objects.filter(id=idx)

    #  put must queryset or get_queryset
    # @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        params = request.data
        try:
            c = self.get_queryset(request.GET.dict().get('id'))
            if c:
                c.update(template=params['template'])
            result = {'status': 0, 'error': ''}
            resp_status = status.HTTP_200_OK
        except Exception as e:
            result = {'status': 1, 'error': str(e)}
            resp_status = status.HTTP_200_OK
        return Response(result, status=resp_status)

