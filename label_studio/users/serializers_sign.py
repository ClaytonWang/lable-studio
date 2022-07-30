#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : serializers_sign.py
  > CreateTime : 2022/7/29 15:08
"""
from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.serializers import SerializerMethodField
from users.serializers import UserSimpleSerializer
from users.models import SignUpInvite
from users.serializers import UserSimpleSerializer


class SignUpInviteListSerializer(serializers.ModelSerializer):
    """
    """
    class Meta:
        model = SignUpInvite
        fields = '__all__'


class SignUpInviteDetailSerializer(SignUpInviteListSerializer):
    class Meta:
        model = SignUpInvite
        fields = '__all__'


class SignUpInviteCreateSerializer(serializers.ModelSerializer):

    group_id = serializers.IntegerField(required=True)
    organization_id = serializers.IntegerField(required=True)
    code = serializers.CharField(required=True)

    class Meta:
        model = SignUpInvite
        fields = '__all__'


class SignUpInviteUpdateSerializer(SignUpInviteCreateSerializer):

    """
    """
    pass
