# Generated by Django 3.1.14 on 2022-07-28 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model_manager', '0003_auto_20220727_0917'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelmanager',
            name='model_parameter',
            field=models.JSONField(default=dict, help_text='模型入参数', null=True, verbose_name='run model parameter'),
        ),
        migrations.AddField(
            model_name='modelmanager',
            name='model_result',
            field=models.CharField(default='', help_text='模型入参数', max_length=140, null=True, verbose_name='run model result url'),
        ),
        migrations.AddField(
            model_name='modelmanager',
            name='state',
            field=models.IntegerField(choices=[(1, '初始'), (2, '训练'), (3, '训练'), (4, '完成'), (5, '异常')], default=1, null=True, verbose_name='model state'),
        ),
        migrations.AlterField(
            model_name='modelmanager',
            name='type',
            field=models.CharField(choices=[('intention', '对话意图分类'), ('generation', '对话生成'), ('clean', '清洗模型')], default=None, max_length=50, null=True, verbose_name='model type'),
        ),
        migrations.AlterField(
            model_name='modelmanager',
            name='version',
            field=models.TextField(blank=True, default='1.0', help_text='Machine learning model version', null=True, verbose_name='model version'),
        ),
    ]