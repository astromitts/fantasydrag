# Generated by Django 3.2.4 on 2021-06-29 01:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0020_alter_participant_episodes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wildcardappearance',
            name='appearance_type',
        ),
        migrations.RemoveField(
            model_name='wildcardappearance',
            name='point_value',
        ),
    ]
