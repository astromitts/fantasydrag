# Generated by Django 3.2.4 on 2021-07-01 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0027_panel_draft_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='panel',
            name='draft_rules',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
