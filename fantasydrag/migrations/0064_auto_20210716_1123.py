# Generated by Django 3.2.4 on 2021-07-16 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0063_alter_queen_normalized_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='defaultrule',
            name='drag_race_type',
            field=models.CharField(choices=[('standard', 'standard'), ('international', 'international'), ('allstars', 'all stars')], default='standard', max_length=100),
        ),
        migrations.AddField(
            model_name='rule',
            name='drag_race_type',
            field=models.CharField(choices=[('standard', 'standard'), ('international', 'international'), ('allstars', 'all stars')], default='standard', max_length=100),
        ),
    ]
