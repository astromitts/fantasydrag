# Generated by Django 3.2.4 on 2021-07-16 11:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0070_auto_20210716_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultrule',
            name='drag_race_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.dragracetype'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='drag_race_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.dragracetype'),
        ),
    ]