# Generated by Django 3.2.4 on 2021-07-14 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0046_alter_panel_panel_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='panel',
            name='panel_type',
            field=models.CharField(choices=[('private', 'Private'), ('public', 'Public')], default='private', max_length=25),
        ),
    ]
