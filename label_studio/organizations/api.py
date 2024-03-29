"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
from rest_framework import status
from django.urls import reverse
from django.conf import settings
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator
from django.conf import settings

from label_studio.core.permissions import all_permissions, ViewClassPermission
from label_studio.core.utils.common import get_object_with_check_and_log, bool_from_request

from organizations.models import Organization
from organizations.serializers import (
    OrganizationSerializer, OrganizationIdSerializer, OrganizationMemberUserSerializer, OrganizationInviteSerializer
)
from organizations.serializers import OrganizationCreatedSerializer
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated


logger = logging.getLogger(__name__)


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Organizations'],
        operation_summary='List your organizations',
        operation_description="""
        Return a list of the organizations you've created or that you have access to.
        """
    ))
class OrganizationListAPI(generics.ListCreateAPIView):
    queryset = Organization.objects.all().order_by('-created_at')
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = ViewClassPermission(
        GET=all_permissions.organizations_view,
        PUT=all_permissions.organizations_change,
        POST=all_permissions.organizations_create,
        PATCH=all_permissions.organizations_change,
        DELETE=all_permissions.organizations_change,
    )
    serializer_class = OrganizationIdSerializer

    def get_object(self):
        org = get_object_with_check_and_log(self.request, Organization, pk=self.kwargs[self.lookup_field])
        self.check_object_permissions(self.request, org)
        return org

    # 获取已经关联用户的组织
    # def filter_queryset(self, queryset):
        # return queryset.filter(users=self.request.user).distinct()

    def get(self, request, *args, **kwargs):
        return super(OrganizationListAPI, self).get(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def post(self, request, *args, **kwargs):
        data = request.POST.dict()
        if not data:
            data = request.data
        data['created_by'] = request.user.id
        serializer = OrganizationCreatedSerializer(data=data)
        # serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class OrganizationMemberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'

    def get_page_size(self, request):
        # emulate "unlimited" page_size
        if self.page_size_query_param in request.query_params and request.query_params[self.page_size_query_param] == '-1':
            return 1000000
        return super().get_page_size(request)


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Organizations'],
        operation_summary='Get organization members list',
        operation_description='Retrieve a list of the organization members and their IDs.',
        manual_parameters=[
            openapi.Parameter(
                name='id',
                type=openapi.TYPE_INTEGER,
                in_=openapi.IN_PATH,
                description='A unique integer value identifying this organization.'),
        ],
    ))
class OrganizationMemberListAPI(generics.ListAPIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_required = ViewClassPermission(
        GET=all_permissions.organizations_view,
        PUT=all_permissions.organizations_change,
        PATCH=all_permissions.organizations_change,
        DELETE=all_permissions.organizations_change,
    )
    serializer_class = OrganizationMemberUserSerializer
    pagination_class = OrganizationMemberPagination

    def get_serializer_context(self):
        return {
            'contributed_to_projects': bool_from_request(self.request.GET, 'contributed_to_projects', False)
        }

    def get_queryset(self):
        org = generics.get_object_or_404(self.request.user.organizations, pk=self.kwargs[self.lookup_field])
        return org.members.order_by('user__username')


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['Organizations'],
        operation_summary=' Get organization settings',
        operation_description='Retrieve the settings for a specific organization by ID.'
    ))
@method_decorator(name='patch', decorator=swagger_auto_schema(
        tags=['Organizations'],
        operation_summary='Update organization settings',
        operation_description='Update the settings for a specific organization by ID.'
    ))
class OrganizationAPI(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    queryset = Organization.objects.all()
    permission_required = all_permissions.organizations_change
    serializer_class = OrganizationSerializer

    redirect_route = 'organizations-dashboard'
    redirect_kwarg = 'pk'

    def get_object(self):
        org = generics.get_object_or_404(self.queryset, pk=self.kwargs[
            self.lookup_field])
        self.check_object_permissions(self.request, org)
        return org

    def get(self, request, *args, **kwargs):
        return super(OrganizationAPI, self).get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        # self.queryset = Organization.objects.filter(pk=kwargs.get('pk'))
        return super(OrganizationAPI, self).patch(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return super(OrganizationAPI, self).put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.users.count() or instance.projects.count():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=dict(error='组织有关联的用户或项目。')
            )
        return super(OrganizationListAPI, self).delete(request, *args, **kwargs)


@method_decorator(name='get', decorator=swagger_auto_schema(
        tags=["Invites"],
        operation_summary='Get organization invite link',
        operation_description='Get a link to use to invite a new member to an organization in Label Studio Enterprise.',
        responses={200: OrganizationInviteSerializer()}
    ))
class OrganizationInviteAPI(APIView):
    parser_classes = (JSONParser,)
    permission_required = all_permissions.organizations_change

    def get(self, request, *args, **kwargs):
        org = get_object_with_check_and_log(self.request, Organization, pk=request.user.active_organization_id)
        self.check_object_permissions(self.request, org)
        invite_url = '{}?token={}'.format(reverse('user-signup'), org.token)
        if hasattr(settings, 'FORCE_SCRIPT_NAME') and settings.FORCE_SCRIPT_NAME:
            invite_url = invite_url.replace(settings.FORCE_SCRIPT_NAME, '', 1)
        serializer = OrganizationInviteSerializer(data={'invite_url': invite_url, 'token': org.token})
        serializer.is_valid()
        return Response(serializer.data, status=200)


@method_decorator(name='post', decorator=swagger_auto_schema(
        tags=["Invites"],
        operation_summary='Reset organization token',
        operation_description='Reset the token used in the invitation link to invite someone to an organization.',
        responses={200: OrganizationInviteSerializer()}
    ))
class OrganizationResetTokenAPI(APIView):
    permission_required = all_permissions.organizations_invite
    parser_classes = (JSONParser,)

    def post(self, request, *args, **kwargs):
        org = request.user.active_organization
        org.reset_token()
        logger.debug(f'New token for organization {org.pk} is {org.token}')
        invite_url = '{}?token={}'.format(reverse('user-signup'), org.token)
        serializer = OrganizationInviteSerializer(data={'invite_url': invite_url, 'token': org.token})
        serializer.is_valid()
        return Response(serializer.data, status=201)


"""
"""


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organization_all(request):
    """
    :param request:
    :return:
    """
    data = request.data
    queryset = Organization.objects.values('id', 'title')
    return Response(data=list(queryset))


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def organization_change(request):
    """
    :param request:
    :return:
    """
    data = request.POST.dict()
    if not data:
        data = request.data
    o_id = data.get('organization_id')
    if not o_id:
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data=dict(error='必须传组织参数')
        )
    try:
        o_id = int(o_id)
    except Exception as e:
        logger.warning('organization_id: ', o_id, ' message:', str(e))
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data=dict(error='组织参数是整型')
        )

    query = Organization.objects.filter(id=o_id).first()
    request.user.active_organization = query
    request.user.save()
    return Response(data=dict(message=f"更新成{query.title}"))