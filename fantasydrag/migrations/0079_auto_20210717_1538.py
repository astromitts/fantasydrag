# Generated by Django 3.2.4 on 2021-07-17 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0078_remove_rule_drag_race'),
    ]

    operations = [
        migrations.AddField(
            model_name='dragrace',
            name='open_for_panels',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Rule',
        ),
    ]
