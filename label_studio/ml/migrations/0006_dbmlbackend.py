# Generated by Django 3.1.14 on 2022-06-07 11:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0017_auto_20220607_1106'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ml', '0005_auto_20211010_1344'),
    ]

    operations = [
        migrations.CreateModel(
            name='DbMLBackend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField(help_text='URL for the machine learning model server', verbose_name='url')),
                ('error_message', models.TextField(blank=True, help_text='Error message in error state', null=True, verbose_name='error_message')),
                ('title', models.TextField(blank=True, default='default', help_text='Name of the machine learning backend', null=True, verbose_name='title')),
                ('description', models.TextField(blank=True, default='', help_text='Description for the machine learning backend', null=True, verbose_name='description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_db_ml', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_db_ml', to='projects.project')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_db_ml', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
