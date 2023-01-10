"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import copy
import logging
from rest_framework import status
import drf_yasg.openapi as openapi

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.authtoken.models import Token
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import MethodNotAllowed

from core.permissions import all_permissions, ViewClassPermission
from users.models import User
from users.serializers import UserSerializer
from users.functions import check_avatar
from django.contrib.auth.models import Group
from organizations.models import Organization


logger = logging.getLogger(__name__)


@method_decorator(name='update', decorator=swagger_auto_schema(
    tags=['Users'],
    operation_summary='Save user details',
    operation_description="""
    Save details for a specific user, such as their name or contact information, in Label Studio.
    """,
    manual_parameters=[
        openapi.Parameter(
            name='id',
            type=openapi.TYPE_INTEGER,
            in_=openapi.IN_PATH,
            description='User ID'),
    ],
    request_body=UserSerializer
))
@method_decorator(name='list', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='List users',
        operation_description='List the users that exist on the Label Studio server.'
    ))
@method_decorator(name='create', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Create new user',
        operation_description='Create a user in Label Studio.',
        request_body=UserSerializer
    ))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Get user info',
        operation_description='Get info about a specific Label Studio user, based on the user ID.',
        manual_parameters = [
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='User ID'),
                ],
    ))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Update user details',
        operation_description="""
        Update details for a specific user, such as their name or contact information, in Label Studio.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='User ID'),
        ],
        request_body=UserSerializer
    ))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Delete user',
        operation_description='Delete a specific Label Studio user.',
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='User ID'),
        ],
    ))
class UserAPI(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.organizations_view,
        PUT=all_permissions.organizations_change,
        POST=all_permissions.organizations_change,
        PATCH=all_permissions.organizations_view,
        DELETE=all_permissions.organizations_change,
    )
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    def get_queryset(self):
        return User.objects.filter(organizations=self.request.user.active_organization)

    @swagger_auto_schema(auto_schema=None, methods=['delete', 'post'])
    @action(detail=True, methods=['delete', 'post'], permission_required=all_permissions.avatar_any)
    def avatar(self, request, pk):
        if request.method == 'POST':
            avatar = check_avatar(request.FILES)
            request.user.avatar = avatar
            request.user.save()
            return Response({'detail': 'avatar saved'}, status=200)

        elif request.method == 'DELETE':
            request.user.avatar = None
            request.user.save()
            return Response(status=204)

    def update(self, request, *args, **kwargs):
        return super(UserAPI, self).update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        return super(UserAPI, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if request.user.group != 'admin':
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=dict(error=f'普通用户没有权限创建用户')
            )

        data = copy.deepcopy(request.data)
        email = data.get('email')

        group = Group.objects.filter(id=data.get('group', -1)).first()
        if not group or not email:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=dict(error=f'指定角色或邮箱错误')
            )

        data['username'] = data.get('email').split('@')[0]
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        password = data.get('password')
        serializer.instance.set_password(password)
        # 用户添加角色
        serializer.instance.groups.add(group)
        serializer.instance.save()
        # 添加组织成员
        org = Organization.objects.filter(title='Label Studio').first()
        if org:
            serializer.instance.active_organization_id = org.id
            serializer.instance.save()
            org.users.add(serializer.instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        return super(UserAPI, self).retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        old_pwd = request.data.get('old_pwd')
        new_pwd = request.data.get('new_pwd')
        if old_pwd and new_pwd:
            if not instance.check_password(old_pwd):
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data=dict(error=f'旧密码错误')
                )
            instance.set_password(new_pwd)
            instance.save()
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        return super(UserAPI, self).destroy(request, *args, **kwargs)

    @action(methods=['GET'], detail=False)
    def all(self, request, *args, **kwargs):
        """
        查询指定分组用户，且带出该用户分配的项目
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        group = request.GET.dict().get('group')
        if not group:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=dict(error=f'必须指定角色')
            )
        queryset = User.objects.filter(
            groups__name=group,
            active_organization=request.user.active_organization
        ).values(
            'id', 'email', 'username', 'first_name', 'last_name',
            'org_project__id'
        )
        result = {}
        for query in queryset:
            u_id = query['id']
            p_id = query.pop('org_project__id')
            p_ids = [p_id] if p_id else []
            if u_id not in result:
                query['project_ids'] = p_ids
            else:
                query['project_ids'] = result[u_id]['project_ids'] + p_ids
            result[u_id] = query

        return Response(data=list(result.values()))

    @action(methods=['POST'], detail=False)
    def update_user_group(self, request):
        """
        指定用户设置分组    一个用户只有一个角色（分组）
        :param request:
        :return:
        """
        from django.contrib.auth.models import Group
        data = request.data
        user_id = data.get('user_id')
        group_id = data.get('group_id')
        user = User.objects.filter(id=user_id).first()
        group = Group.objects.filter(id=group_id)
        if not group:
            return Response(
                status=400,
                data=dict(detail=f'指定用户组不存在')
            )

        if user.groups.all():
            user.groups.remove()

        user.groups.add(group)
        return Response(status=201, data=dict(msg='更新成功'))


@method_decorator(name='post', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Reset user token',
        operation_description='Reset the user token for the current user.',
        responses={
            201: openapi.Response(
                description='User token response',
                schema=openapi.Schema(
                    description='User token',
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(
                            description='Token',
                            type=openapi.TYPE_STRING
                        )
                    }
                ))
        }))
class UserResetTokenAPI(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        token = user.reset_token()
        logger.debug(f'New token for user {user.pk} is {token.key}')
        return Response({'token': token.key}, status=201)


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Get user token',
        operation_description='Get a user token to authenticate to the API as the current user.',
        responses={
            200: openapi.Response(
                description='User token response',
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(
                        description='Token',
                        type=openapi.TYPE_STRING
                    )
                }
            )
        }))
class UserGetTokenAPI(APIView):
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        user = request.user
        token = Token.objects.get(user=user)
        return Response({'token': str(token)}, status=200)


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Users'],
        operation_summary='Retrieve my user',
        operation_description='Retrieve details of the account that you are using to access the API.'
    ))
class UserWhoAmIAPI(generics.RetrieveAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return super(UserWhoAmIAPI, self).get(request, *args, **kwargs)
