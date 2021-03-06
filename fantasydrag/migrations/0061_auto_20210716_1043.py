# Generated by Django 3.2.4 on 2021-07-16 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0060_auto_20210716_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='queen',
            name='normalized_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='queen',
            name='main_franchise',
            field=models.CharField(choices=[('US', 'US'), ('Australia', 'Down Under'), ('UK', 'UK'), ('Canada', 'Canada')], db_index=True, default='US', max_length=100),
        ),
        migrations.AlterField(
            model_name='queen',
            name='name',
            field=models.CharField(db_index=True, max_length=100, unique=True),
        ),
    ]
