# Generated by Django 3.2.5 on 2021-07-18 15:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legal', '0002_auto_20210718_1535'),
    ]

    operations = [
        migrations.RenameField(
            model_name='policy',
            old_name='privacy_polivy',
            new_name='privacy_policy',
        ),
    ]
