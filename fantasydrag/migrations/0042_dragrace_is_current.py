# Generated by Django 3.2.4 on 2021-07-12 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0041_panel_normalized_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='dragrace',
            name='is_current',
            field=models.BooleanField(default=False),
        ),
    ]