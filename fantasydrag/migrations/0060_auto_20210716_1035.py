# Generated by Django 3.2.4 on 2021-07-16 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0059_auto_20210716_1029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queen',
            name='tier_score',
            field=models.DecimalField(db_index=True, decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AlterField(
            model_name='queen',
            name='total_score',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]