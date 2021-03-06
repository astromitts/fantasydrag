# Generated by Django 3.2.4 on 2021-06-24 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0006_auto_20210624_1603'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='panel',
            name='draft_order',
        ),
        migrations.AddField(
            model_name='panel',
            name='draft_data',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='panel',
            name='status',
            field=models.CharField(choices=[('open', 'open'), ('in draft', 'in draft'), ('active', 'active'), ('closed', 'closed')], default='open', max_length=25),
        ),
    ]
