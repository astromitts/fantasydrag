# Generated by Django 3.2.5 on 2021-07-18 15:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('legal', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userlog',
            old_name='eula_timestamp',
            new_name='timestamp',
        ),
        migrations.RemoveField(
            model_name='userlog',
            name='pp_timestamp',
        ),
        migrations.AddField(
            model_name='userlog',
            name='policy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='legal.policy'),
        ),
    ]
