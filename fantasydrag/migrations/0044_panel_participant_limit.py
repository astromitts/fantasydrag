# Generated by Django 3.2.4 on 2021-07-13 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0043_auto_20210713_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='panel',
            name='participant_limit',
            field=models.IntegerField(default=1),
        ),
    ]
