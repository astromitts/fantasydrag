# Generated by Django 3.2.5 on 2021-07-27 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0004_auto_20210727_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='canonicalqueendragracescore',
            name='total_score',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='canonicalqueenepisodescore',
            name='total_score',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='panelistdragracescore',
            name='total_score',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='panelistepisodescore',
            name='total_score',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='queendragracescore',
            name='total_score',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='queenepisodescore',
            name='total_score',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
