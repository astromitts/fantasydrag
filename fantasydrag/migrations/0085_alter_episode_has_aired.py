# Generated by Django 3.2.4 on 2021-07-18 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0084_episode_has_aired'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='has_aired',
            field=models.BooleanField(default=False),
        ),
    ]