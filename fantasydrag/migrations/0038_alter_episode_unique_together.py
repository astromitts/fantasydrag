# Generated by Django 3.2.4 on 2021-07-10 00:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0037_alter_queen_name'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='episode',
            unique_together={('drag_race', 'number')},
        ),
    ]
