# Generated by Django 3.1.14 on 2022-08-05 04:02

import data_import.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_import', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='file',
            field=models.FileField(upload_to=data_import.models.upload_name_generator),
        ),
    ]