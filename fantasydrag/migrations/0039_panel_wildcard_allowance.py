# Generated by Django 3.2.4 on 2021-07-11 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0038_alter_episode_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='panel',
            name='wildcard_allowance',
            field=models.IntegerField(default=0, help_text='The number of wildcard queens each player can draft'),
        ),
    ]
