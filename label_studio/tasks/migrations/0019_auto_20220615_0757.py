# Generated by Django 3.1.14 on 2022-06-15 07:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0017_auto_20220607_1106'),
        ('tasks', '0018_auto_20220615_0534'),
    ]

    operations = [
        migrations.RenameField(
            model_name='taskdbalgorithm',
            old_name='source_text',
            new_name='source',
        ),
        migrations.AlterField(
            model_name='taskdbalgorithm',
            name='project',
            field=models.ForeignKey(help_text='Project ID for this task', on_delete=django.db.models.deletion.CASCADE, related_name='project_tag', to='projects.project'),
        ),
        migrations.AlterField(
            model_name='taskdbalgorithm',
            name='task',
            field=models.ForeignKey(default=1, help_text='Corresponding task for this annotation', on_delete=django.db.models.deletion.CASCADE, related_name='task_tag', to='tasks.task'),
            preserve_default=False,
        ),
    ]
