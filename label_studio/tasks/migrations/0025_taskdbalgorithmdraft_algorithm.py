# Generated by Django 3.1.14 on 2022-07-08 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0024_auto_20220708_0451'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskdbalgorithmdraft',
            name='algorithm',
            field=models.JSONField(blank=True, null=True, verbose_name='算法清洗'),
        ),
    ]