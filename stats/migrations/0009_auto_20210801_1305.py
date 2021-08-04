# Generated by Django 3.2.5 on 2021-08-01 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0008_dragracedraftscores_episodedraftscores'),
    ]

    operations = [
        migrations.AddField(
            model_name='canonicalqueendragracescore',
            name='eliminated_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='canonicalqueendragracescore',
            name='lipsync_wins',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='canonicalqueendragracescore',
            name='main_wins',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='canonicalqueendragracescore',
            name='mini_wins',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='canonicalqueendragracescore',
            name='safe_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='queendragracescore',
            name='eliminated_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='queendragracescore',
            name='lipsync_wins',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='queendragracescore',
            name='main_wins',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='queendragracescore',
            name='mini_wins',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='queendragracescore',
            name='safe_count',
            field=models.IntegerField(default=0),
        ),
    ]