# Generated by Django 3.1.14 on 2022-07-30 02:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_signupinvite'),
    ]

    operations = [
        migrations.AddField(
            model_name='signupinvite',
            name='signup_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='to_invite', to=settings.AUTH_USER_MODEL, verbose_name='sign up user'),
        ),
        migrations.AddField(
            model_name='signupinvite',
            name='state',
            field=models.BooleanField(default=False, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='signupinvite',
            name='code',
            field=models.CharField(max_length=10, unique=True, verbose_name='Verification Code'),
        ),
    ]
