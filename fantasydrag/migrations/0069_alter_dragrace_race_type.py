# Generated by Django 3.2.4 on 2021-07-16 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0068_populate_drag_race_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dragrace',
            name='race_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.dragracetype'),
        ),
    ]
