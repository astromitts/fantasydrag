# Generated by Django 3.2.4 on 2021-07-14 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0048_auto_20210714_0154'),
    ]

    operations = [
        migrations.AddField(
            model_name='panel',
            name='draft_order',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='panel',
            name='draft_rounds',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='panel',
            name='total_drafts',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='participant',
            name='episodes',
            field=models.ManyToManyField(blank=True, to='fantasydrag.Episode'),
        ),
    ]
