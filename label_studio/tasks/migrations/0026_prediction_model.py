# Generated by Django 3.1.14 on 2022-11-02 02:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('model_manager', '0016_auto_20221102_0256'),
        ('tasks', '0025_taskdbalgorithmdraft_algorithm'),
    ]

    operations = [
        migrations.AddField(
            model_name='prediction',
            name='model',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='model_manager.modelmanager'),
        ),
    ]
