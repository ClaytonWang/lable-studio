# Generated by Django 3.1.14 on 2022-12-20 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model_manager', '0019_auto_20221220_0236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelmanager',
            name='url',
            field=models.TextField(blank=True, help_text='URL for the machine learning model server', null=True, verbose_name='url'),
        ),
    ]
