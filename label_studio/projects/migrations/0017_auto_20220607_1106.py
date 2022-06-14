# Generated by Django 3.1.14 on 2022-06-07 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0016_auto_20220211_2218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='control_weights',
            field=models.JSONField(default=dict, help_text="Dict of weights for each control tag in metric calculation. Each control tag (e.g. label or choice) will have it's own key in control weight dict with weight for each label and overall weight.For example, if bounding box annotation with control tag named my_bbox should be included with 0.33 weight in agreement calculation, and the first label Car should be twice more important than Airplaine, then you have to need the specify: {'my_bbox': {'type': 'RectangleLabels', 'labels': {'Car': 1.0, 'Airplaine': 0.5}, 'overall': 0.33}", null=True, verbose_name='control weights'),
        ),
    ]
