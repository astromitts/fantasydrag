# Generated by Django 3.2.4 on 2021-07-06 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0036_custom_fill_default_rules'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queen',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
