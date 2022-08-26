# Generated by Django 3.1.14 on 2022-08-25 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0025_taskdbalgorithmdraft_algorithm'),
        ('model_manager', '0011_auto_20220825_0551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modeltrain',
            name='assessment_task',
            field=models.ManyToManyField(blank=True, default=None, null=True, related_name='model_assessment', to='tasks.Task'),
        ),
        migrations.AlterField(
            model_name='modeltrain',
            name='train_task',
            field=models.ManyToManyField(blank=True, default=None, null=True, related_name='model_train', to='tasks.Task'),
        ),
    ]
