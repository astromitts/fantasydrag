# Generated by Django 3.2.4 on 2021-07-17 22:00

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('flags', '0002_alter_featureflag_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='featureflag',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]