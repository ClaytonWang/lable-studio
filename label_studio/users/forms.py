"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import os
import logging

from datetime import datetime
from django import forms
from django.contrib import auth
from django.conf import settings

from users.models import User
from users.models import SignUpInvite
from datetime import timedelta


SIGNUP_INVITE_CODE_LENGTH = 6
EMAIL_MAX_LENGTH = 256
PASS_MAX_LENGTH = 64
PASS_MIN_LENGTH = 8
USERNAME_MAX_LENGTH = 30
DISPLAY_NAME_LENGTH = 100
USERNAME_LENGTH_ERR = 'Please enter a username 30 characters or fewer in length'
DISPLAY_NAME_LENGTH_ERR = 'Please enter a display name 100 characters or fewer in length'
PASS_LENGTH_ERR = '请输入8-12位长度的密码'
INVALID_USER_ERROR = 'The email and password you entered don\'t match.'

logger = logging.getLogger(__name__)


class LoginForm(forms.Form):
    """ For logging in to the app and all - session based
    """
    # use username instead of email when LDAP enabled
    email = forms.CharField(label='User') if settings.USE_USERNAME_FOR_LOGIN\
        else forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self, *args, **kwargs):
        cleaned = super(LoginForm, self).clean()
        email = cleaned.get('email', '').lower()
        password = cleaned.get('password', '')
        if len(email) >= EMAIL_MAX_LENGTH:
            raise forms.ValidationError('邮箱太长')

        # advanced way for user auth
        user = settings.USER_AUTH(User, email, password)

        # regular access
        if user is None:
            user = auth.authenticate(email=email, password=password)

        if user and user.is_active:
            return {'user': user}
        else:
            raise forms.ValidationError(INVALID_USER_ERROR)


class UserSignupForm(forms.Form):
    code = forms.CharField(label="Code",
                           max_length=SIGNUP_INVITE_CODE_LENGTH,
                           error_messages={'required': '注册验证码不能为空'})
    email = forms.EmailField(label="Work Email", error_messages={'required': '邮箱错误'})
    password = forms.CharField(max_length=PASS_MAX_LENGTH,
                               error_messages={'required': PASS_LENGTH_ERR},
                               widget=forms.TextInput(attrs={'type': 'password'}))

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < PASS_MIN_LENGTH:
            raise forms.ValidationError(PASS_LENGTH_ERR)
        return password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username.lower()).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if len(email) >= EMAIL_MAX_LENGTH:
            raise forms.ValidationError('邮箱太长')

        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已存在')

        return email

    def clean_code(self):
        code = self.cleaned_data.get('code')
        invite = SignUpInvite.objects.filter(code=code).first()
        if not invite:
            raise forms.ValidationError('请填写有效的验证码')

        if invite.state:
            raise forms.ValidationError(f'{code}已经被注册')

        invite_update_time = invite.updated_at.replace(tzinfo=None)
        expire_time = invite_update_time + timedelta(
            seconds=settings.SIGNUP_INVITE_EXPIRE_TIME
        )
        if datetime.now() > expire_time:
            raise forms.ValidationError('邀请链接已经过期')

        return code

    def save(self):
        cleaned = self.cleaned_data
        password = cleaned['password']
        email = cleaned['email'].lower()
        user = User.objects.create_user(email, password)
        return user


class UserProfileForm(forms.ModelForm):
    """ This form is used in profile account pages
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone')

