# Generated by Django 3.2.5 on 2021-07-27 12:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fantasydrag', '0101_auto_20210727_1248'),
        ('stats', '0002_panelistdragracescore_drag_race'),
    ]

    operations = [
        migrations.CreateModel(
            name='CanonicalQueenEpisodeScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_score', models.IntegerField(default=0)),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.episode')),
                ('queen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.queen')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CanonicalQueenDragRaceScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_score', models.IntegerField(default=0)),
                ('drag_race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.dragrace')),
                ('queen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasydrag.queen')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
