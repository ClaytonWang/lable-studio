# Generated by Django 3.1.14 on 2022-08-03 02:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0023_project_template_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='set',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='project_set', to='projects.projectset'),
        ),
    ]
