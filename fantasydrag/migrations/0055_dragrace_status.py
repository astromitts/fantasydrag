# Generated by Django 3.2.4 on 2021-07-15 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0054_auto_20210714_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='dragrace',
            name='status',
            field=models.CharField(choices=[('open', 'open'), ('active', 'active'), ('closed', 'closed')], default='open', max_length=25),
        ),
    ]