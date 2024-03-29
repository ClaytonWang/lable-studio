#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : api_train.py
  > CreateTime : 2022/8/2 16:32
"""
import os
import math
import json
import logging
from django.db.models import F, Q
from django.db.transaction import atomic
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from model_manager.serializers_train import ModelTrainListSerializer
from model_manager.serializers_train import ModelTrainDetailSerializer
from model_manager.serializers_train import ModelTrainCreateSerializer
from model_manager.serializers_train import ModelTrainAccuracySerializer
from .serializers import ModelManagerDetailSerializer
from model_manager.models import ModelTrain, ModelManager
from projects.models import ProjectSet, Project
from tasks.models import Task, Annotation, Prediction
from db_ml.common import DbPageNumberPagination
from db_ml.common import MultiSerializerViewSetMixin
from db_ml.services import get_choice_values
from db_ml.services import train_model
from db_ml.services import generate_uuid
from core.utils.common import create_hash
from projects.services import get_template
from db_ml.services import get_first_version_model
from db_ml.services import get_project_labels
from db_ml.services import INTENT_DIALOG_PROMPT_TOKEN
from db_ml.listener_result import thread_read_redis_celery_result
from .serializers import ModelManagerCreateSerializer
from model_manager.serializers_train import ModelTrainUpdateSerializer


logger = logging.getLogger(__name__)


class ModelTrainViews(MultiSerializerViewSetMixin, ModelViewSet):
    serializer_action_classes = {
        'list': ModelTrainListSerializer,
        'retrieve': ModelTrainDetailSerializer,
        'create': ModelTrainCreateSerializer,
        # 'update': ModelTrainUpdateSerializer,
        # 'partial_update': ModelTrainUpdateSerializer,
    }
    pagination_class = DbPageNumberPagination

    def list(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return: dict
        """
        filter_keys = ['project_id', 'model_id', 'user_id', 'project_set_id', 'is_train']
        data = request.GET.dict()
        filter_params = dict()
        for key in filter_keys:
            value = data.get(key)
            if not value:
                continue
            if key == 'user_id':
                filter_params['created_by_id'] = value
            elif key == 'project_set_id':
                filter_params['project__set_id'] = value
            elif key == 'is_train':
                if value == 'true':
                    filter_params['is_train'] = True
                elif value == 'false':
                    filter_params['is_train'] = False
            else:
                filter_params[key] = value
        if not filter_params.get('project_id'):
            raise Exception('必须指定项目')

        self.queryset = ModelTrain.objects.filter(**filter_params).order_by('-created_at')
        return super(ModelTrainViews, self).list(request, *args, **kwargs)

    @action(methods=['GET'], detail=False)
    def ltrain(self, request):
        project_id = request.GET.dict().get('project_id')
        category = request.GET.dict().get('category', 'train')
        query = ModelTrain.objects.filter(
            project_id=project_id, category=category
        ).order_by('-id').first()
        if query:
            serializer = ModelTrainDetailSerializer(query)
            data = serializer.data
            return Response(data)
        else:
            return Response({})

    @action(methods=['GET'], detail=False)
    def select(self, request, *args, **kwargs):
        project_id = request.GET.dict().get('project_id')
        model_query = self.get_model_of_project(project_id)
        models = model_query.distinct('title', 'version')
        users = ModelTrain.objects.annotate(
            user_id=F('created_by__id'), username=F('created_by__username')
        ).filter(project_id=project_id)\
            .values('user_id', 'username').distinct('username')
        project_set = ProjectSet.objects.filter(project_set__id=project_id).values(
            'id', 'title'
        ).distinct()

        result = dict(
            models=list(models),
            users=list(users),
            train=[{True: '是'}, {False: '否'}],
            project_sets=list(project_set),
        )

        return Response(status=status.HTTP_200_OK, data=result)

    @action(methods=['GET'], detail=False)
    def model(self, request, *args, **kwargs):
        """
        选取 对话意图分类 对话生成 的模型
        模型的选择，选择模型的project_id是null的model或是project_id等于当前项目的project_id
        :return:
        """
        project_id = request.GET.dict().get('project_id')
        # _type = request.GET.dict().get('type')
        data = self.get_model_of_project(project_id)
        return Response(data=list(data))

    @action(methods=['GET'], detail=False)
    def config(self, request, *args, **kwargs):
        with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
            data = json.loads(f.read())
            return Response(data=data)

    @action(methods=['GET'], detail=False)
    def init(self, request, *args, **kwargs):
        """
        新增评估&新增训练的初始数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        params = request.GET.dict()
        model_id = params.get('model_id')
        project_id = params.get('project_id')
        operate = params.get('operate', 'assessment')

        project = Project.objects.filter(id=project_id).first()
        if project.template_type not in ('intent-classification', 'conversational-generation'):
            raise Exception('项目模版类型错误，支持模版是对话意图识别&对话生成。')

        tasks = Task.objects.filter(project_id=project_id)

        # anno_result, pre_result = self.get_project_label_result(tasks)
        # # TODO 手动标注和自动标注，历史数据引起的错误
        # exactness_count, error_count, total_count, accuracy_rate = 0, 0, 0, 0
        # for task_id, result in pre_result.items():
        #     if task_id not in anno_result:
        #         exactness_count += 1
        #         continue
        #
        #     pre_labels = get_choice_values(result)
        #     ann_labels = get_choice_values(anno_result[task_id])
        #     if ann_labels == pre_labels:
        #         exactness_count += 1
        #         continue
        #
        #     error_count += 1

        task_count = tasks.count()
        result = dict(
            model_id=model_id,
            project_id=project_id,
            project_title=project.title,
            total_count=task_count,
            exactness_count=0,  # exactness_count,
            accuracy_rate=0,  # round(exactness_count/task_count, 2),
        )

        if operate == 'train':
            version, new_version = self.get_model_version(project, is_init=True)
            result['version'] = version
            result['new_version'] = new_version

        return Response(data=result)

    @action(methods=['GET'], detail=True)
    def accuracy(self, request, *args, **kwargs):
        model_id = kwargs.get('pk')
        # if not model_id:
        #     train = ModelTrain.objects.fitler(id=kwargs.get('pk')).first()
        #     model_id = train.model.id

        train = ModelTrain.objects.filter(model_id=model_id).all()
        serializer = ModelTrainAccuracySerializer(instance=train, many=True)
        data = serializer.data
        # .values(
        # 'model__title', 'model__version', 'project__title',
        # 'accuracy_rate', 'created_at', 'created_by'
        # )
        result = []
        # for item in queryset:
        #     pass
            # item['created_by'] = UserSimpleSerializer(instance=)
        return Response(data=list(data))

    def check_task_label_in_project(self, project_id, task_query):
        # 有手动标注取手动标注的值，没有取自动标注的值
        # labels = get_project_labels(project_id)
        anno_result, pre_result = self.get_project_label_result(task_query)
        task_label = {}
        for item in task_query:
            task_id = item.id
            label = ''
            if task_id in anno_result:
                label = get_choice_values(anno_result.get(str(task_id)))

            if not label and str(task_id) in pre_result:
                label = get_choice_values(pre_result.get(str(task_id)))

            if isinstance(label, list):
                label = ''.join(label)

            task_label[task_id] = label
        return True, task_label

    def get_dialogue_data(self, task_query):

        anno_result, pre_result = self.get_project_label_result(task_query)
        task_label = []
        for task in task_query:

            _index = 0
            result = []
            task_id = str(task.id)
            if task_id in anno_result:
                result = anno_result.get(task_id, [])
            if not result and task_id in pre_result:
                result = pre_result.get(task_id, [])

            for item in result:
                text = item.get('value', {}).get('text', [])
                if not text:
                    continue
                item = dict(
                    task_id=f'{task_id}_{_index}',
                    dialogue=[{'text': item, 'author': ''} for item in text],
                    label=item.get('from_name')
                )
                task_label.append(item)
                _index += 1
        return task_label

    @action(methods=['POST'], detail=False)
    def train(self, request, *args, **kwargs):
        """
        新增训练接口
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = self.get_train_assessment_params(request)
        model_id = data.get('model_id')
        project_id = data.get('project_id')
        project = Project.objects.filter(id=project_id).first()
        model = ModelManager.objects.filter(id=model_id).first()
        if not model:
            return Response(status=400, data=dict(message='未查询到有效模型'))

        # train
        version, new_version = self.get_model_version(project=project, is_init=False, model=model)
        train_data = dict()
        train_data['state'] = 3
        train_data['category'] = 'train'
        train_data['is_train'] = True
        train_data['project_id'] = project_id
        train_data['model_id'] = model_id
        train_data['created_by_id'] = request.user.id
        train_data['model_title'] = model.title

        # 判断标签是否一致
        task_query = Task.objects.filter(project_id=data.get('project_id')).order_by('-id')

        template_type = None
        if len(task_query):
            template_type = task_query[0].project.template_type

        with atomic():
            # train_count 前端在init接口拿到数据，训练模型带回来
            train_data['total_count'] = task_query.count()
            new_train = self.created_train(train_data)

            # 拼接模型服务参数
            task_data = []

            # 建模型管理记录
            serializer = ModelManagerDetailSerializer(instance=model)
            model_data = dict()
            model_data['model'] = model
            model_data['state'] = 3
            model_data['base'] = False
            model_data['version'] = new_version
            model_data['hash_id'] = create_hash()
            model_data['title'] = model.title
            model_data['model_parameter'] = data.get('model_params')
            model_data['created_by'] = request.user
            model_data['project_id'] = project_id

            for field in [
                'url', 'type', 'labels',
                'organization', 'model_type',
            ]:
                model_data[field] = getattr(serializer.instance, field)

            new_model = ModelManager.objects.create(**model_data)
            if new_model and new_train:
                new_train.new_model = new_model
                new_train.save()

            # 调用模型服务
            if template_type == 'intent-classification':
                # 意图标注
                _, task_label = self.check_task_label_in_project(data.get('project_id'), task_query)
                for item in task_query:
                    task_id = item.id
                    dialogue = item.data.get('dialogue', [])
                    task_data.append(dict(
                        task_id=task_id,
                        dialogue=dialogue,
                        label=task_label[task_id],
                    ))
            else:
                # 对话生成
                task_data = self.get_dialogue_data(task_query)

            obj_id = new_train.id
            _uuid = generate_uuid('train', obj_id)

        templates = get_template(project_id)
        _state, text = train_model(
                project_id=data.get('project_id'),
                model=model,
                new_model=new_model,
                task_data=task_data,
                _uuid=_uuid,
                template=templates,
                model_parameter=new_train.model_parameter
            )

        if not _state:
            new_train.delete()
            new_model.delete()
        else:
            thread_read_redis_celery_result(data.get('project_id'), 'train', new_train)

        train_serializer = ModelTrainDetailSerializer(instance=new_train)
        headers = self.get_success_headers(train_serializer.data)
        return Response(train_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['POST'], detail=False)
    def assessment(self, request, *args, **kwargs):
        """
        废弃 评估功能废弃（2022-12-17）
        新增评估接口
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        post_data = self.get_train_assessment_params(request)
        obj_data = self.created_train(post_data)
        headers = self.get_success_headers(obj_data)
        return Response(post_data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['GET'], detail=True)
    def finished(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        # state = 4 是训练完成
        if ModelTrain.objects.filter(id=pk, is_train=True, state=4).exists():
            return Response(data=dict(is_finished=True))
        else:
            return Response(data=dict(is_finished=False))

    @staticmethod
    def get_project_label_result(tasks):
        anno_query = Annotation.objects.filter(task__in=tasks)
        anno_result = {str(item.task_id): item.result for item in anno_query}
        pre_query = Prediction.objects.filter(task__in=tasks)
        pre_result = {str(item.task_id): item.result for item in pre_query}

        return anno_result, pre_result

    @staticmethod
    def get_model_of_project(project_id, _type=None):
        if isinstance(_type, str) and _type:
            _type = [_type]
        else:
            _type = ('intention', 'generation', 'annotation')

        queryset = ModelManager.objects.filter(
            Q(type__in=_type, project_id__isnull=True) |
            Q(project_id__id=project_id)
        ).values('id', 'title', 'version')
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.queryset = ModelTrain.objects.filter(pk=kwargs.get('pk'))
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        return Response(data)

    @staticmethod
    def get_model_version(project, is_init=False, model=None):
        """
            - 同一项目中，根据迭代前的模型版本号，每触发一次人在环路迭代，版本号+1，如：
            - 创建项目时选择“训练新模型”，即1.0版本的基础模型。触发第一次人在环路后，迭代的模型版本号为2.0。触发第二次人在环路后（不论选择的是1.0版还是2.0版），迭代的模型版本号为3.0。
            - 创建项目时选择“训练已有模型”，如某个4.0版本的模型。触发第一次人在环路后，迭代的模型版本号为5.0。触发第二次人在环路后（不论选择的是2.0~5.0的哪个版本），迭代的模型版本号为6.0。
        """

        version, new_version = '1.0', '2.0'
        if project.model:
            version = project.model.version

        max_version_model = ModelManager.objects.filter(project=project).values('version')
        max_version_model = list(max_version_model)
        if max_version_model:
            max_version_model.sort(key=lambda k: int(float(k['version'])), reverse=True)
            max_version = max_version_model[0]['version']
        else:
            # 训练已经有模型，没有纪录取关联模型，新版本在当前版本加1
            if project.model:
                max_version = project.model.version
            else:
                max_version = version
        new_version = str(format(float(max_version) + 1, '.1f'))

        # 训练新模型：
        # if not project.model:
        #     return '1.0', '2.0'
        #
        # if is_init and project:
        #     version = project.model.version
        #     new_version = str(format(float(version) + 1, '.1f'))
        #     return version, new_version
        #
        # if not is_init and project:
        #
        #     max_version_model = ModelManager.objects.filter(project=project).values('version')
        #     max_version_model = list(max_version_model)
        #     if max_version_model:
        #         max_version_model.sort(key=lambda k: int(float(k['version'])), reverse=True)
        #         version = max_version_model[0]['version']
        #     else:
        #         # 训练已经有模型，没有纪录取关联模型，新版本在当前版本加1
        #         version = project.model.version
        #     new_version = str(format(float(version) + 1, '.1f'))
        return version, new_version

    def created_train(self, data):
        model_id = data.get('model_id')
        if 'model_id' in data and model_id is None or model_id == '':
            data.pop('model_id')

        if model_id:
            model = ModelManager.objects.filter(id=data.get('model_id')).first()
            if model:
                data['model_title'] = model.title
            data.pop('model_id')
        serializer = ModelTrainCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        new_train = ModelTrain.objects.create(**serializer.data)
        # self.perform_create(serializer)
        return new_train

    @staticmethod
    def get_train_assessment_params(request):
        data = request.POST.dict()
        if not data:
            data = request.data

        if not data.get('project_id'):
            raise Exception('必须指定项目')

        data['category'] = 'assessment'
        data['created_by_id'] = request.user.id
        data['updated_by_id'] = request.user.id
        data['organization_id'] = request.user.active_organization.id
        return data

    def destroy(self, request, *args, **kwargs):
        self.queryset = ModelTrain.objects.filter(pk=kwargs.get('pk'))
        if len(self.queryset) and self.queryset[0].category != 'assessment':
            raise Exception('只能删除评估模型')
        super(ModelTrainViews, self).destroy(request, *args, **kwargs)
        return Response(status=200, data=dict(message='删除成功'))
